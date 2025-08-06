"use client";

import React, { useRef } from 'react';
import { dadmsTheme } from '../../design-system/theme';
import { Icon } from '../shared/Icon';
import { useOntologyWorkspaceStore } from './store';

interface OntologyToolbarProps {
    className?: string;
    isPropertiesPanelOpen?: boolean;
    isExternalPanelOpen?: boolean;
    onTogglePropertiesPanel?: () => void;
    onToggleExternalPanel?: () => void;
}

const OntologyToolbar: React.FC<OntologyToolbarProps> = ({
    className,
    isPropertiesPanelOpen = false,
    isExternalPanelOpen = false,
    onTogglePropertiesPanel,
    onToggleExternalPanel
}) => {
    const {
        activeOntology,
        isValidating,
        validateOntology,
        loadMockWorkspace,
        generateMockOntology,
        clearSelection,
        selectedNodes,
        selectedEdges,
        saveOntologyToFile,
        loadOntologyFromFile,
        createNewOntology,
    } = useOntologyWorkspaceStore();

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleNewOntology = () => {
        createNewOntology();
    };

    const handleSave = () => {
        if (activeOntology) {
            saveOntologyToFile();
        }
    };

    const handleImport = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            loadOntologyFromFile(file);
        }
        // Reset the input so the same file can be selected again
        event.target.value = '';
    };

    const handleExport = () => {
        // Use the same save functionality for now
        handleSave();
    };

    const handleValidate = () => {
        validateOntology();
    };

    const handleGenerateAAS = () => {
        generateMockOntology();
    };

    const handleClearSelection = () => {
        clearSelection();
    };

    const handleLoadMockData = () => {
        loadMockWorkspace();
    };

    const handleClearStorage = () => {
        if (confirm('Clear all saved ontology data from browser storage?')) {
            localStorage.removeItem('ontology-workspace-store');
            window.location.reload();
        }
    };

    const containerStyle = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: `${dadmsTheme.spacing.sm} ${dadmsTheme.spacing.md}`,
        background: dadmsTheme.colors.background.secondary,
        borderBottom: `1px solid ${dadmsTheme.colors.border.default}`,
        gap: dadmsTheme.spacing.md,
        fontFamily: dadmsTheme.typography.fontFamily.default,
        height: '48px', // Fixed compact height
    };

    const leftSectionStyle = {
        display: 'flex',
        alignItems: 'center',
        gap: dadmsTheme.spacing.sm,
    };

    const rightSectionStyle = {
        display: 'flex',
        alignItems: 'center',
        gap: dadmsTheme.spacing.sm,
    };

    const buttonStyle = (variant: 'primary' | 'secondary' | 'warning' = 'secondary', disabled = false) => ({
        padding: `${dadmsTheme.spacing.xs} ${dadmsTheme.spacing.sm}`,
        background: 'transparent',
        border: 'none',
        borderRadius: dadmsTheme.borderRadius.sm,
        color: disabled
            ? dadmsTheme.colors.text.muted
            : variant === 'primary'
                ? dadmsTheme.colors.accent.primary
                : variant === 'warning'
                    ? dadmsTheme.colors.accent.warning
                    : dadmsTheme.colors.text.primary,
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontSize: dadmsTheme.typography.fontSize.sm,
        fontWeight: dadmsTheme.typography.fontWeight.medium,
        transition: dadmsTheme.transitions.fast,
        opacity: disabled ? 0.6 : 1,
        display: 'flex',
        alignItems: 'center',
        gap: dadmsTheme.spacing.xs,
        '&:hover': {
            background: dadmsTheme.colors.background.tertiary,
        },
    });

    const titleStyle = {
        fontSize: dadmsTheme.typography.fontSize.md,
        fontWeight: dadmsTheme.typography.fontWeight.semibold,
        color: dadmsTheme.colors.text.primary,
        marginRight: dadmsTheme.spacing.md,
    };

    const statusStyle = {
        display: 'flex',
        alignItems: 'center',
        gap: dadmsTheme.spacing.xs,
        fontSize: dadmsTheme.typography.fontSize.xs,
        color: dadmsTheme.colors.text.secondary,
    };

    const dividerStyle = {
        width: '1px',
        height: '24px',
        background: dadmsTheme.colors.border.default,
        margin: `0 ${dadmsTheme.spacing.sm}`,
    };

    return (
        <div style={containerStyle} className={className}>
            {/* Hidden file input for importing ontologies */}
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".json"
                style={{ display: 'none' }}
            />

            <div style={leftSectionStyle}>
                <div style={titleStyle}>
                    {activeOntology?.name || 'Ontology Modeler'}
                </div>

                <button
                    style={buttonStyle('secondary')}
                    onClick={handleNewOntology}
                    title="Create new ontology"
                >
                    <Icon name="add" size="sm" color={dadmsTheme.colors.text.primary} />
                    New
                </button>

                <button
                    style={buttonStyle('secondary')}
                    onClick={handleImport}
                    title="Import ontology from file"
                >
                    <Icon name="arrow-down" size="sm" color={dadmsTheme.colors.text.primary} />
                    Import
                </button>

                <button
                    style={buttonStyle('primary', !activeOntology)}
                    onClick={handleSave}
                    disabled={!activeOntology}
                    title="Save current ontology"
                >
                    <Icon name="save" size="sm" color={!activeOntology ? dadmsTheme.colors.text.muted : dadmsTheme.colors.accent.primary} />
                    Save
                </button>

                <button
                    style={buttonStyle('secondary', !activeOntology)}
                    onClick={handleExport}
                    disabled={!activeOntology}
                    title="Export ontology"
                >
                    <Icon name="arrow-up" size="sm" color={!activeOntology ? dadmsTheme.colors.text.muted : dadmsTheme.colors.text.primary} />
                    Export
                </button>

                <div style={dividerStyle} />

                <button
                    style={buttonStyle('warning', !activeOntology || isValidating)}
                    onClick={handleValidate}
                    disabled={!activeOntology || isValidating}
                    title="Validate ontology consistency"
                >
                    <Icon name={isValidating ? "loading" : "check"} size="sm" color={!activeOntology || isValidating ? dadmsTheme.colors.text.muted : dadmsTheme.colors.accent.warning} />
                    {isValidating ? 'Validating...' : 'Validate'}
                </button>

                <button
                    style={buttonStyle('secondary')}
                    onClick={handleGenerateAAS}
                    title="Generate ontology using AAS (AI Assistant)"
                >
                    <Icon name="robot" size="sm" color={dadmsTheme.colors.text.primary} />
                    Generate via AAS
                </button>

                <div style={dividerStyle} />

                <button
                    style={buttonStyle('secondary')}
                    onClick={handleLoadMockData}
                    title="Load example ontology for testing"
                >
                    <Icon name="project" size="sm" color={dadmsTheme.colors.text.primary} />
                    Load Example
                </button>

                <button
                    style={buttonStyle('secondary')}
                    onClick={handleClearStorage}
                    title="Clear browser storage and refresh"
                >
                    <Icon name="trash" size="sm" color={dadmsTheme.colors.text.primary} />
                    Clear Storage
                </button>

                {(selectedNodes.length > 0 || selectedEdges.length > 0) && (
                    <>
                        <div style={dividerStyle} />
                        <button
                            style={buttonStyle('secondary')}
                            onClick={handleClearSelection}
                            title="Clear current selection"
                        >
                            ✖ Clear Selection
                        </button>
                    </>
                )}
            </div>

            <div style={rightSectionStyle}>
                {/* Panel Toggle Buttons */}
                {onTogglePropertiesPanel && onToggleExternalPanel && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: dadmsTheme.spacing.xs }}>
                        <button
                            style={{
                                ...buttonStyle('secondary'),
                                color: isPropertiesPanelOpen ? dadmsTheme.colors.accent.primary : dadmsTheme.colors.text.secondary,
                            }}
                            onClick={onTogglePropertiesPanel}
                            title="Toggle properties panel"
                        >
                            <Icon name="settings-gear" size="sm" color={isPropertiesPanelOpen ? dadmsTheme.colors.accent.primary : dadmsTheme.colors.text.secondary} />
                        </button>
                        <button
                            style={{
                                ...buttonStyle('secondary'),
                                color: isExternalPanelOpen ? dadmsTheme.colors.accent.primary : dadmsTheme.colors.text.secondary,
                            }}
                            onClick={onToggleExternalPanel}
                            title="Toggle external references panel"
                        >
                            <Icon name="references" size="sm" color={isExternalPanelOpen ? dadmsTheme.colors.accent.primary : dadmsTheme.colors.text.secondary} />
                        </button>
                        <div style={dividerStyle} />
                    </div>
                )}

                <div style={statusStyle}>
                    {activeOntology && (
                        <>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: dadmsTheme.spacing.xs,
                                fontSize: dadmsTheme.typography.fontSize.xs,
                                color: dadmsTheme.colors.text.secondary,
                            }}>
                                <Icon name="project" size="xs" color={dadmsTheme.colors.text.secondary} />
                                {activeOntology.nodes.length} nodes

                                <Icon name="type-hierarchy" size="xs" color={dadmsTheme.colors.text.secondary} />
                                {activeOntology.edges.length} edges
                            </div>
                            {(selectedNodes.length > 0 || selectedEdges.length > 0) && (
                                <div style={{ color: dadmsTheme.colors.accent.info }}>
                                    ({selectedNodes.length + selectedEdges.length} selected)
                                </div>
                            )}
                            <div style={dividerStyle} />
                            <div style={{ color: dadmsTheme.colors.status.active }}>
                                v{activeOntology.version}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default OntologyToolbar; 