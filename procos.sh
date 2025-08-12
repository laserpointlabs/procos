#!/usr/bin/env bash
set -euo pipefail

# ProcOS lifecycle script (start/stop/restart/status/logs/test/down/help)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs/start"
KERNEL_LOG="$ROOT_DIR/logs/kernel/kernel.log"
PID_FILE="$LOG_DIR/kernel.pid"
READINESS_FILE="${KERNEL_READINESS_FILE:-/tmp/procos.ready}"
CAMUNDA_BASE_URL=${CAMUNDA_BASE_URL:-http://localhost:8080}
HEALTH_TIMEOUT_SEC=${HEALTH_TIMEOUT_SEC:-180}

mkdir -p "$LOG_DIR"

print_step() { echo -e "\n\033[1;34m==> $1\033[0m"; }
print_ok()   { echo -e "\033[1;32m✔ $1\033[0m"; }
print_warn() { echo -e "\033[1;33m⚠ $1\033[0m"; }
print_err()  { echo -e "\033[1;31m✖ $1\033[0m"; }

ensure_env() {
  if [[ ! -f "$ROOT_DIR/.env" ]]; then
    if [[ -f "$ROOT_DIR/env.example" ]]; then
      cp "$ROOT_DIR/env.example" "$ROOT_DIR/.env"
      print_ok ".env created from env.example"
    else
      print_err "env.example not found; cannot scaffold .env"
      exit 1
    fi
  fi
}

docker_up() {
  print_step "Build and start Docker services"
  docker compose version >/dev/null 2>&1 || { print_err "docker compose not installed"; exit 1; }
  docker compose up -d --build | tee "$LOG_DIR/compose_up.log"
}

docker_down() {
  print_step "Stopping Docker services"
  docker compose down | tee "$LOG_DIR/compose_down.log" || true
}

docker_stop() {
  print_step "Stopping Docker services (compose stop)"
  docker compose stop | tee "$LOG_DIR/compose_stop.log" || true
}

wait_camunda() {
  print_step "Waiting for Camunda at $CAMUNDA_BASE_URL (timeout ${HEALTH_TIMEOUT_SEC}s)"
  start_ts=$(date +%s)
  attempt=0
  until curl -sf "$CAMUNDA_BASE_URL/engine-rest/engine" >/dev/null 2>&1; do
    attempt=$((attempt+1))
    now=$(date +%s)
    elapsed=$((now - start_ts))
    if (( elapsed > HEALTH_TIMEOUT_SEC )); then
      print_err "Camunda did not become ready in ${HEALTH_TIMEOUT_SEC}s"
      docker compose ps | tee "$LOG_DIR/compose_ps_on_timeout.log" || true
      return 1
    fi
    if (( attempt % 10 == 0 )); then
      echo -n "."
    fi
    sleep 3
  done
  echo
  print_ok "Camunda REST is reachable"
}

start_kernel() {
  print_step "Starting microkernel"
  mkdir -p "$(dirname "$KERNEL_LOG")"
  if [[ -f "$PID_FILE" ]] && ps -p "$(cat "$PID_FILE" 2>/dev/null)" >/dev/null 2>&1; then
    print_warn "Kernel already running (pid=$(cat "$PID_FILE"))"
    return 0
  fi
  python3 -u "$ROOT_DIR/src/microkernel/procos_kernel.py" >> "$KERNEL_LOG" 2>&1 &
  KERNEL_PID=$!
  echo "$KERNEL_PID" > "$PID_FILE"
  print_ok "Microkernel started (pid=$KERNEL_PID). Logs: $KERNEL_LOG"

  print_step "Waiting for kernel readiness marker: $READINESS_FILE"
  for _ in {1..60}; do
    if [[ -f "$READINESS_FILE" ]]; then
      print_ok "Kernel readiness marker present"
      break
    fi
    sleep 2
  done
}

stop_kernel() {
  print_step "Stopping microkernel"
  if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || true)
    if [[ -n "${PID:-}" ]] && ps -p "$PID" >/dev/null 2>&1; then
      kill -TERM "$PID" || true
      for _ in {1..20}; do
        if ps -p "$PID" >/dev/null 2>&1; then sleep 0.5; else break; fi
      done
      if ps -p "$PID" >/dev/null 2>&1; then
        print_warn "Kernel did not stop on TERM; sending KILL"
        kill -KILL "$PID" || true
      fi
      print_ok "Kernel stopped"
    else
      print_warn "No running kernel process found"
    fi
    rm -f "$PID_FILE"
  else
    print_warn "PID file not found"
  fi
}

quick_test() {
  print_step "Quick health test"
  local ok=0
  if curl -sf "$CAMUNDA_BASE_URL/engine-rest/engine" >/dev/null; then
    print_ok "Camunda engine endpoint OK"
    ok=$((ok+1))
  else
    print_err "Camunda engine endpoint FAILED"
  fi
  if curl -sf "$CAMUNDA_BASE_URL/engine-rest/version" >/dev/null; then
    print_ok "Camunda version endpoint OK"
    ok=$((ok+1))
  else
    print_warn "Camunda version endpoint not available"
  fi
  if [[ -f "$READINESS_FILE" ]]; then
    print_ok "Kernel readiness marker present"
    ok=$((ok+1))
  else
    print_warn "Kernel readiness marker not found"
  fi
  return $([[ $ok -ge 2 ]] && echo 0 || echo 1)
}

status() {
  print_step "Status"
  echo "Compose services:"
  docker compose ps | cat || true
  echo
  echo "Camunda health:"
  if curl -sf "$CAMUNDA_BASE_URL/engine-rest/engine" >/dev/null; then
    echo "- engine endpoint: OK"
  else
    echo "- engine endpoint: FAIL"
  fi
  echo
  if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || true)
    if [[ -n "${PID:-}" ]] && ps -p "$PID" >/dev/null 2>&1; then
      echo "Kernel: RUNNING (pid=$PID)"
    else
      echo "Kernel: NOT RUNNING (stale pid file)"
    fi
  else
    echo "Kernel: NOT RUNNING"
  fi
  [[ -f "$READINESS_FILE" ]] && echo "Readiness: PRESENT" || echo "Readiness: ABSENT"
}

logs() {
  print_step "Kernel logs"
  local follow="${1:-}"
  if [[ ! -f "$KERNEL_LOG" ]]; then
    print_warn "No kernel log yet at $KERNEL_LOG"
    return 0
  fi
  if [[ "$follow" == "-f" || "$follow" == "--follow" ]]; then
    tail -n 200 -f "$KERNEL_LOG"
  else
    tail -n 200 "$KERNEL_LOG"
  fi
}

usage() {
  cat <<USAGE
Usage: $(basename "$0") <command>

Commands:
  start      Ensure env, up docker, wait Camunda, start kernel
  stop       Stop kernel only
  stack-start  Start docker compose stack only (no kernel)
  stack-stop   Stop docker compose stack (containers stopped, not removed)
  restart    Stop then start kernel (docker unchanged)
  down       docker compose down (stop services)
  status     Show docker/camunda/kernel status
  logs [-f]  Show kernel logs (follow with -f)
  test       Run quick health tests (camunda + kernel readiness)
  help       Show this help

Notes:
  - On WSL, ensure Ollama on port 11434 is reachable to avoid port hangs.
USAGE
}

# WSL/Ollama hint (non-fatal)
if grep -qi microsoft /proc/version 2>/dev/null; then
  print_warn "WSL detected. Ensure Ollama port 11434 is free and service reachable."
fi

cmd="${1:-start}"
case "$cmd" in
  start)
    ensure_env
    docker_up
    wait_camunda
    start_kernel
    quick_test || true
    ;;
  stop)
    stop_kernel
    ;;
  stack-start)
    ensure_env
    docker_up
    wait_camunda || true
    ;;
  stack-stop)
    docker_stop
    ;;
  restart)
    stop_kernel
    start_kernel
    quick_test || true
    ;;
  down)
    stop_kernel || true
    docker_down
    ;;
  status)
    status
    ;;
  logs)
    shift || true
    logs "${1:-}"
    ;;
  test)
    quick_test
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    print_err "Unknown command: $cmd"
    usage
    exit 1
    ;;
esac

print_ok "Done"


