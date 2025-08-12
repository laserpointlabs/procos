# Legacy Workers

This directory contains the older external task workers (generic and AI). The
current architecture shifts to PDO/TDE/DAS where execution is BPMN-first. Do
not add new code here; migrate functionality into BPMN tasks (TDEs) with
adapters under `src/tde/` or script tasks referenced by BPMN.
