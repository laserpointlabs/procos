"use client";

import React, { useCallback, useRef, useState } from 'react';
import ReactFlow, {
    addEdge,
    Background,
    BackgroundVariant,
    Connection,
    ConnectionMode,
    Controls,
    Edge,
    EdgeTypes,
    MiniMap,
    Node,
    NodeChange,
    NodeTypes,
    ReactFlowProvider,
    useEdgesState,
    useNodesState,
    useReactFlow
} from 'reactflow';
import 'reactflow/dist/style.css';

import { usePanel } from '../../contexts/PanelStateContext';
import { dadmsTheme } from '../../design-system/theme';
import { edgeTypes } from './edges';
import { nodeTypes } from './nodes';
import { useOntologyWorkspaceStore } from './store';
import { DADMSRelationshipType, OntologyEdge, OntologyNode } from './types';

// Relationship Type Selector Component
interface RelationshipSelectorProps {
    isVisible: boolean;
    position: { x: number; y: number };
    onSelect: (relationshipType: DADMSRelationshipType) => void;
    onCancel: () => void;
}

const RelationshipSelector: React.FC<RelationshipSelectorProps> = ({
    isVisible,
    position,
    onSelect,
    onCancel
}) => {
    const [customRelationship, setCustomRelationship] = useState('');
    const [showCustomInput, setShowCustomInput] = useState(false);

    // Use persistent panel states for relationship groups
    const customGroup = usePanel('relationship-custom');
    const decisionGroup = usePanel('relationship-decision');
    const organizationalGroup = usePanel('relationship-organizational');
    const basicGroup = usePanel('relationship-basic');

    // Get custom relationship types from store
    const { activeOntology, addCustomRelationshipType } = useOntologyWorkspaceStore();
    const customRelationshipTypes = activeOntology?.customRelationshipTypes || [];

    // Helper function to format custom relationship type labels
    const formatCustomTypeLabel = (type: string) => {
        return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    // Debug logging
    React.useEffect(() => {
        if (isVisible) {
            console.log('RelationshipSelector opened');
            console.log('Active ontology:', activeOntology?.name);
            console.log('Custom relationship types:', customRelationshipTypes);
            setCustomRelationship('');
            setShowCustomInput(false);
        }
    }, [isVisible, activeOntology, customRelationshipTypes]);

    const relationshipGroups = [
        {
            title: "Custom Relationships",
            isCustom: true,
            relationships: customRelationshipTypes.map(type => ({
                type: type,
                label: formatCustomTypeLabel(type),
                description: 'Custom relationship type'
            }))
        },
        {
            title: "Decision Intelligence",
            relationships: [
                { type: 'influences' as const, label: 'Influences', description: 'One entity influences another' },
                { type: 'depends_on' as const, label: 'Depends On', description: 'One entity depends on another' },
                { type: 'conflicts_with' as const, label: 'Conflicts With', description: 'Entities are in conflict' },
                { type: 'supports_decision' as const, label: 'Supports Decision', description: 'Supports a decision' },
            ]
        },
        {
            title: "Organizational",
            relationships: [
                { type: 'has_stakeholder' as const, label: 'Has Stakeholder', description: 'Has a stakeholder' },
                { type: 'has_responsibility' as const, label: 'Has Responsibility', description: 'Has responsibility for' },
                { type: 'manages' as const, label: 'Manages', description: 'Manages or oversees' },
                { type: 'reports_to' as const, label: 'Reports To', description: 'Reports to' },
            ]
        },
        {
            title: "Basic",
            relationships: [
                { type: 'relates_to' as const, label: 'Relates To', description: 'General relationship' },
                { type: 'has_property' as const, label: 'Has Property', description: 'Has a property' },
                { type: 'part_of' as const, label: 'Part Of', description: 'Is part of' },
            ]
        }
    ];

    const handleCustomSubmit = () => {
        if (customRelationship.trim()) {
            // Convert custom string to valid relationship type format
            const customType = customRelationship.trim().toLowerCase().replace(/\s+/g, '_') as DADMSRelationshipType;

            console.log('Creating custom relationship type:', customType);

            // Add to the ontology's custom relationship types if it doesn't exist
            if (!customRelationshipTypes.includes(customType)) {
                addCustomRelationshipType(customType);
            }

            onSelect(customType);
            setCustomRelationship('');
            setShowCustomInput(false);
        }
    };

    const toggleGroup = (groupTitle: string) => {
        switch (groupTitle) {
            case 'Custom Relationships':
                customGroup.toggleCollapsed();
                break;
            case 'Decision Intelligence':
                decisionGroup.toggleCollapsed();
                break;
            case 'Organizational':
                organizationalGroup.toggleCollapsed();
                break;
            case 'Basic':
                basicGroup.toggleCollapsed();
                break;
        }
    };

    if (!isVisible) return null;

    return (
        <div style={{
            position: 'absolute',
            left: position.x,
            top: position.y,
            background: dadmsTheme.colors.background.elevated,
            border: `1px solid ${dadmsTheme.colors.border.default}`,
            borderRadius: dadmsTheme.borderRadius.lg,
            boxShadow: dadmsTheme.shadows.lg,
            zIndex: dadmsTheme.zIndex.modal,
            minWidth: '320px',
            maxHeight: '500px',
            overflowY: 'auto',
            fontFamily: dadmsTheme.typography.fontFamily.default,
        }}>
            <div style={{
                padding: dadmsTheme.spacing.md,
                borderBottom: `1px solid ${dadmsTheme.colors.border.default}`,
                background: dadmsTheme.colors.background.secondary,
                borderRadius: `${dadmsTheme.borderRadius.lg} ${dadmsTheme.borderRadius.lg} 0 0`,
            }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                }}>
                    <h3 style={{
                        margin: 0,
                        fontSize: dadmsTheme.typography.fontSize.md,
                        fontWeight: dadmsTheme.typography.fontWeight.semibold,
                        color: dadmsTheme.colors.text.primary,
                    }}>Select Relationship Type</h3>
                    <button
                        onClick={onCancel}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: dadmsTheme.colors.text.secondary,
                            fontSize: dadmsTheme.typography.fontSize.lg,
                        }}
                    >
                        ×
                    </button>
                </div>
            </div>

            {/* Custom Relationship Input */}
            <div style={{ padding: dadmsTheme.spacing.sm }}>
                {showCustomInput ? (
                    <div style={{
                        padding: dadmsTheme.spacing.sm,
                        background: dadmsTheme.colors.background.primary,
                        border: `1px solid ${dadmsTheme.colors.accent.primary}`,
                        borderRadius: dadmsTheme.borderRadius.md,
                        marginBottom: dadmsTheme.spacing.sm,
                    }}>
                        <h4 style={{
                            margin: `0 0 ${dadmsTheme.spacing.xs} 0`,
                            fontSize: dadmsTheme.typography.fontSize.sm,
                            fontWeight: dadmsTheme.typography.fontWeight.medium,
                            color: dadmsTheme.colors.text.primary,
                        }}>Custom Relationship</h4>
                        <div style={{ display: 'flex', gap: dadmsTheme.spacing.xs }}>
                            <input
                                type="text"
                                value={customRelationship}
                                onChange={(e) => setCustomRelationship(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleCustomSubmit();
                                    if (e.key === 'Escape') setShowCustomInput(false);
                                }}
                                placeholder="e.g., 'owns', 'created by', 'similar to'"
                                style={{
                                    flex: 1,
                                    padding: dadmsTheme.spacing.xs,
                                    border: `1px solid ${dadmsTheme.colors.border.default}`,
                                    borderRadius: dadmsTheme.borderRadius.sm,
                                    fontSize: dadmsTheme.typography.fontSize.sm,
                                }}
                                autoFocus
                            />
                            <button
                                onClick={handleCustomSubmit}
                                disabled={!customRelationship.trim()}
                                style={{
                                    padding: `${dadmsTheme.spacing.xs} ${dadmsTheme.spacing.sm}`,
                                    background: dadmsTheme.colors.accent.success,
                                    color: dadmsTheme.colors.text.inverse,
                                    border: 'none',
                                    borderRadius: dadmsTheme.borderRadius.sm,
                                    cursor: customRelationship.trim() ? 'pointer' : 'not-allowed',
                                    fontSize: dadmsTheme.typography.fontSize.sm,
                                }}
                            >
                                Create
                            </button>
                            <button
                                onClick={() => setShowCustomInput(false)}
                                style={{
                                    padding: dadmsTheme.spacing.xs,
                                    background: dadmsTheme.colors.background.secondary,
                                    border: `1px solid ${dadmsTheme.colors.border.default}`,
                                    borderRadius: dadmsTheme.borderRadius.sm,
                                    cursor: 'pointer',
                                    fontSize: dadmsTheme.typography.fontSize.sm,
                                }}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                ) : (
                    <button
                        onClick={() => setShowCustomInput(true)}
                        style={{
                            width: '100%',
                            padding: dadmsTheme.spacing.sm,
                            background: dadmsTheme.colors.accent.primary,
                            color: dadmsTheme.colors.text.inverse,
                            border: 'none',
                            borderRadius: dadmsTheme.borderRadius.md,
                            cursor: 'pointer',
                            fontSize: dadmsTheme.typography.fontSize.sm,
                            fontWeight: dadmsTheme.typography.fontWeight.medium,
                            marginBottom: dadmsTheme.spacing.sm,
                        }}
                    >
                        + Create Custom Relationship
                    </button>
                )}
            </div>

            {relationshipGroups
                .filter(group => !group.isCustom || group.relationships.length > 0) // Only show custom group if it has relationships
                .map((group) => {
                    const isCollapsed = (() => {
                        switch (group.title) {
                            case 'Custom Relationships':
                                return customGroup.isCollapsed;
                            case 'Decision Intelligence':
                                return decisionGroup.isCollapsed;
                            case 'Organizational':
                                return organizationalGroup.isCollapsed;
                            case 'Basic':
                                return basicGroup.isCollapsed;
                            default:
                                return false;
                        }
                    })();
                    const isCustomGroup = group.isCustom;

                    return (
                        <div key={group.title} style={{ padding: dadmsTheme.spacing.sm }}>
                            <button
                                onClick={() => toggleGroup(group.title)}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    width: '100%',
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    padding: `${dadmsTheme.spacing.xs} 0`,
                                    marginBottom: dadmsTheme.spacing.xs,
                                }}
                            >
                                <h4 style={{
                                    margin: 0,
                                    fontSize: dadmsTheme.typography.fontSize.sm,
                                    fontWeight: dadmsTheme.typography.fontWeight.medium,
                                    color: isCustomGroup ? dadmsTheme.colors.accent.primary : dadmsTheme.colors.text.secondary,
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px',
                                }}>
                                    {group.title} {isCustomGroup && group.relationships.length > 0 && `(${group.relationships.length})`}
                                </h4>
                                <span style={{
                                    fontSize: dadmsTheme.typography.fontSize.sm,
                                    color: dadmsTheme.colors.text.secondary,
                                    transform: isCollapsed ? 'rotate(-90deg)' : 'rotate(0deg)',
                                    transition: dadmsTheme.transitions.fast,
                                }}>
                                    ▼
                                </span>
                            </button>

                            {!isCollapsed && group.relationships.map((rel) => (
                                <button
                                    key={rel.type}
                                    onClick={() => onSelect(rel.type)}
                                    style={{
                                        display: 'block',
                                        width: '100%',
                                        padding: dadmsTheme.spacing.sm,
                                        marginBottom: dadmsTheme.spacing.xs,
                                        background: dadmsTheme.colors.background.primary,
                                        border: `1px solid ${isCustomGroup ? dadmsTheme.colors.accent.secondary : dadmsTheme.colors.border.default}`,
                                        borderRadius: dadmsTheme.borderRadius.md,
                                        cursor: 'pointer',
                                        textAlign: 'left',
                                        transition: dadmsTheme.transitions.fast,
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = dadmsTheme.colors.background.hover;
                                        e.currentTarget.style.borderColor = isCustomGroup ? dadmsTheme.colors.accent.secondary : dadmsTheme.colors.accent.primary;
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = dadmsTheme.colors.background.primary;
                                        e.currentTarget.style.borderColor = isCustomGroup ? dadmsTheme.colors.accent.secondary : dadmsTheme.colors.border.default;
                                    }}
                                >
                                    <div style={{
                                        fontSize: dadmsTheme.typography.fontSize.sm,
                                        fontWeight: dadmsTheme.typography.fontWeight.medium,
                                        color: dadmsTheme.colors.text.primary,
                                        marginBottom: '2px',
                                    }}>{rel.label}</div>
                                    <div style={{
                                        fontSize: dadmsTheme.typography.fontSize.xs,
                                        color: dadmsTheme.colors.text.secondary,
                                    }}>{rel.description}</div>
                                </button>
                            ))}
                        </div>
                    );
                })}
        </div>
    );
};

const OntologyModelerInner: React.FC = () => {
    const { isMinimapVisible } = useOntologyWorkspaceStore();
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const { project } = useReactFlow();

    const {
        activeOntology,
        selectedNodes,
        selectedEdges,
        addNode,
        addEdge: storeAddEdge,
        setSelectedNodes,
        setSelectedEdges,
        updateNode,
        updateEdge,
        deleteNode,
        deleteEdge,
        updateNodePositions,
        addCustomRelationshipType,
    } = useOntologyWorkspaceStore();

    const [nodes, setNodes, onNodesChange] = useNodesState(activeOntology?.nodes || []);
    const [edges, setEdges, onEdgesChange] = useEdgesState(activeOntology?.edges || []);
    const [isConnectionMode, setIsConnectionMode] = useState(false);
    const [pendingConnection, setPendingConnection] = useState<Connection | null>(null);
    const [selectorPosition, setSelectorPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

    // Sync with store when activeOntology changes (but preserve selection during property updates)
    const previousOntologyId = React.useRef<string | null>(null);
    React.useEffect(() => {
        if (activeOntology) {
            // Only reset nodes/edges when switching to a different ontology
            // Don't reset when just updating properties of the same ontology
            if (previousOntologyId.current !== activeOntology.id) {
                console.log('OntologyModeler: Switching to ontology', activeOntology.id);
                setNodes(activeOntology.nodes);
                setEdges(activeOntology.edges);
                previousOntologyId.current = activeOntology.id;
            } else {
                console.log('OntologyModeler: Updating existing ontology properties, preserving React Flow state');
                // Just update the data without resetting React Flow's state
                setNodes(nodes => nodes.map(node => {
                    const storeNode = activeOntology.nodes.find(n => n.id === node.id);
                    return storeNode ? { ...node, data: storeNode.data } : node;
                }));
                setEdges(edges => edges.map(edge => {
                    const storeEdge = activeOntology.edges.find(e => e.id === edge.id);
                    return storeEdge ? { ...edge, data: storeEdge.data } : edge;
                }));
            }
        }
    }, [activeOntology, setNodes, setEdges]);

    // Handle node position changes and persist them
    const onNodeDragStop = useCallback(
        (event: React.MouseEvent, node: Node) => {
            // Update the position in the store
            updateNodePositions([{ id: node.id, position: node.position }]);
        },
        [updateNodePositions],
    );

    // Handle multiple node position changes (for batch updates)
    const onNodesChangeHandler = useCallback(
        (changes: NodeChange[]) => {
            onNodesChange(changes);

            // Check if any changes are position changes
            const positionChanges = changes
                .filter((change): change is NodeChange & { type: 'position'; id: string; position?: { x: number; y: number } } =>
                    change.type === 'position' && 'position' in change && change.position !== undefined
                )
                .map(change => ({
                    id: change.id,
                    position: change.position!
                }));

            if (positionChanges.length > 0) {
                updateNodePositions(positionChanges);
            }
        },
        [onNodesChange, updateNodePositions],
    );

    const onConnect = useCallback(
        (params: Connection | Edge) => {
            // Convert Edge to Connection if needed
            const connection: Connection = 'sourceHandle' in params && params.sourceHandle !== undefined
                ? params as Connection
                : {
                    source: params.source,
                    target: params.target,
                    sourceHandle: params.sourceHandle || null,
                    targetHandle: params.targetHandle || null,
                };

            // Check if this is a note connection (either source or target is a note)
            const sourceNode = nodes.find(n => n.id === connection.source);
            const targetNode = nodes.find(n => n.id === connection.target);
            const isNoteConnection = sourceNode?.type === 'note' || targetNode?.type === 'note';

            if (isNoteConnection) {
                // Automatically create a note connection with dotted line
                const newEdge: OntologyEdge = {
                    ...connection,
                    id: `edge-${Date.now()}`,
                    type: 'note_connection',
                    data: {
                        relationshipType: 'annotates',
                        properties: {},
                        strength: 1.0,
                        isInferred: false,
                        label: 'Note',
                    },
                } as OntologyEdge;

                setEdges((eds) => addEdge(newEdge, eds));
                storeAddEdge(newEdge);
                return;
            }

            // For regular connections, show the relationship selector
            setPendingConnection(connection);

            // Calculate position for the selector (center of the canvas)
            const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
            if (reactFlowBounds) {
                setSelectorPosition({
                    x: reactFlowBounds.width / 2 - 160, // Center horizontally (160 is half of selector width)
                    y: reactFlowBounds.height / 2 - 100, // Center vertically
                });
            } else {
                // Fallback position if bounds are not available
                setSelectorPosition({ x: 200, y: 200 });
            }
        },
        [nodes, setEdges, storeAddEdge],
    );

    const handleRelationshipSelect = useCallback(
        (relationshipType: DADMSRelationshipType) => {
            if (pendingConnection) {
                try {
                    const newEdge: OntologyEdge = {
                        ...pendingConnection,
                        id: `edge-${Date.now()}`,
                        type: 'dadms_relationship',
                        data: {
                            relationshipType,
                            properties: {},
                            strength: 1.0,
                            isInferred: false,
                        },
                    } as OntologyEdge;

                    setEdges((eds) => addEdge(newEdge, eds));
                    storeAddEdge(newEdge);

                    // Automatically select the newly created edge to show its properties
                    setSelectedNodes([]);
                    setSelectedEdges([newEdge.id]);

                    console.log('Successfully created edge:', newEdge);
                } catch (error) {
                    console.error('Error creating edge:', error);
                }
            }

            // Always clear the pending connection and hide selector
            setPendingConnection(null);
        },
        [pendingConnection, setEdges, storeAddEdge, setSelectedNodes, setSelectedEdges],
    );

    const handleRelationshipCancel = useCallback(() => {
        setPendingConnection(null);
        console.log('Relationship creation cancelled');
    }, []);

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event: React.DragEvent) => {
            event.preventDefault();

            const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
            const type = event.dataTransfer.getData('application/reactflow');

            if (typeof type === 'undefined' || !type || !reactFlowBounds) {
                return;
            }

            const position = project({
                x: event.clientX - reactFlowBounds.left,
                y: event.clientY - reactFlowBounds.top,
            });

            // Create better default labels based on type
            const getDefaultLabel = (nodeType: string) => {
                switch (nodeType) {
                    case 'entity':
                        return 'MyEntity';
                    case 'data_property':
                        return 'hasValue';
                    case 'note':
                        return 'Note';
                    default:
                        return 'NewElement';
                }
            };

            const getEntityType = (nodeType: string) => {
                switch (nodeType) {
                    case 'entity':
                        return 'Entity';
                    case 'data_property':
                        return 'Data Property';
                    case 'note':
                        return 'Note';
                    default:
                        return 'Element';
                }
            };

            const getDefaultNoteData = (nodeType: string) => {
                if (nodeType === 'note') {
                    return {
                        noteContent: '',
                        noteType: 'general' as const,
                        noteAuthor: 'DADMS User',
                        noteCreated: new Date().toISOString(),
                        noteLastModified: new Date().toISOString(),
                    };
                }
                return {};
            };

            const newNode: OntologyNode = {
                id: `node-${Date.now()}`,
                type,
                position,
                data: {
                    label: getDefaultLabel(type),
                    entityType: getEntityType(type),
                    properties: {},
                    description: '',
                    ...getDefaultNoteData(type),
                },
            };

            setNodes((nds) => nds.concat(newNode));
            addNode(newNode);

            // Automatically select the newly created node
            setSelectedNodes([newNode.id]);
            setSelectedEdges([]);
        },
        [project, setNodes, addNode, setSelectedNodes, setSelectedEdges],
    );

    const onSelectionChange = useCallback(
        ({ nodes: selectedNodes, edges: selectedEdges }: { nodes: Node[]; edges: Edge[] }) => {
            setSelectedNodes(selectedNodes.map(n => n.id));
            setSelectedEdges(selectedEdges.map(e => e.id));
        },
        [setSelectedNodes, setSelectedEdges],
    );

    const onNodeClick = useCallback(
        (event: React.MouseEvent, node: Node) => {
            console.log('Node clicked:', node);
        },
        [],
    );

    const onEdgeClick = useCallback(
        (event: React.MouseEvent, edge: Edge) => {
            console.log('Edge clicked:', edge);
        },
        [],
    );

    // Handle canvas click to show ontology properties
    const onPaneClick = useCallback(
        (event: React.MouseEvent) => {
            // Clear node and edge selections to show ontology properties
            setSelectedNodes([]);
            setSelectedEdges([]);
            console.log('Canvas clicked - showing ontology properties');
        },
        [setSelectedNodes, setSelectedEdges],
    );

    // Handle node deletion
    const onNodesDelete = useCallback(
        (deletedNodes: Node[]) => {
            deletedNodes.forEach(node => {
                deleteNode(node.id);
                console.log('Deleted node:', node.id);
            });
            // Clear selection after deletion
            setSelectedNodes([]);
            setSelectedEdges([]);
        },
        [deleteNode, setSelectedNodes, setSelectedEdges],
    );

    // Handle edge deletion
    const onEdgesDelete = useCallback(
        (deletedEdges: Edge[]) => {
            deletedEdges.forEach(edge => {
                deleteEdge(edge.id);
                console.log('Deleted edge:', edge.id);
            });
            // Clear selection after deletion
            setSelectedNodes([]);
            setSelectedEdges([]);
        },
        [deleteEdge, setSelectedNodes, setSelectedEdges],
    );

    // Custom styles for DADMS theme
    const reactFlowStyle = {
        background: dadmsTheme.colors.background.primary,
        height: '100%',
        width: '100%',
    };

    const minimapStyle = {
        backgroundColor: dadmsTheme.colors.background.secondary,
        border: `1px solid ${dadmsTheme.colors.border.default}`,
    };

    const controlsStyle = {
        backgroundColor: dadmsTheme.colors.background.secondary,
        border: `1px solid ${dadmsTheme.colors.border.default}`,
        borderRadius: dadmsTheme.borderRadius.md,
    };

    return (
        <div ref={reactFlowWrapper} style={{ height: '100%', width: '100%', position: 'relative' }}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChangeHandler}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onDrop={onDrop}
                onDragOver={onDragOver}
                onSelectionChange={onSelectionChange}
                onNodeClick={onNodeClick}
                onEdgeClick={onEdgeClick}
                onNodeDragStop={onNodeDragStop}
                onPaneClick={onPaneClick}
                onNodesDelete={onNodesDelete}
                onEdgesDelete={onEdgesDelete}
                nodeTypes={nodeTypes as NodeTypes}
                edgeTypes={edgeTypes as EdgeTypes}
                style={reactFlowStyle}
                defaultViewport={{ x: 0, y: 0, zoom: 1 }}
                attributionPosition="bottom-left"
                snapToGrid={true}
                snapGrid={[15, 15]}
                deleteKeyCode="Delete"
                multiSelectionKeyCode="Ctrl"
                panOnScroll={true}
                panOnScrollSpeed={0.5}
                zoomOnScroll={true}
                zoomOnPinch={true}
                zoomOnDoubleClick={false}
                selectNodesOnDrag={false}
                fitView={false}
                connectionMode={ConnectionMode.Loose}
                defaultEdgeOptions={{
                    type: 'dadms_relationship',
                    animated: false,
                    style: { strokeWidth: 2 },
                }}
            >
                <Controls
                    style={controlsStyle}
                    showZoom={true}
                    showFitView={true}
                    showInteractive={true}
                    position="top-left"
                />

                {isMinimapVisible && (
                    <MiniMap
                        style={minimapStyle}
                        nodeColor={(node) => {
                            switch (node.type) {
                                case 'entity':
                                    return dadmsTheme.colors.accent.primary;
                                case 'data_property':
                                    return dadmsTheme.colors.accent.info;
                                case 'note':
                                    return dadmsTheme.colors.accent.secondary;
                                case 'external_reference':
                                    return dadmsTheme.colors.border.light;
                                default:
                                    return dadmsTheme.colors.border.default;
                            }
                        }}
                        nodeStrokeWidth={2}
                        position="bottom-right"
                        pannable={true}
                        zoomable={true}
                    />
                )}

                <Background
                    variant={BackgroundVariant.Dots}
                    gap={20}
                    size={1}
                    color={dadmsTheme.colors.border.default}
                />
            </ReactFlow>

            {/* Relationship Type Selector */}
            <RelationshipSelector
                isVisible={pendingConnection !== null}
                position={selectorPosition}
                onSelect={handleRelationshipSelect}
                onCancel={handleRelationshipCancel}
            />
        </div>
    );
};

const OntologyModeler: React.FC = () => {
    return (
        <ReactFlowProvider>
            <OntologyModelerInner />
        </ReactFlowProvider>
    );
};

export default OntologyModeler; 