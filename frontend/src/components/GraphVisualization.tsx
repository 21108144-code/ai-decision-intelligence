import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
    Node,
    Edge,
    Background,
    Controls,
    MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { CheckCircle, Circle, AlertCircle } from 'lucide-react';
import type { ExecutionResponse } from '@/types';

interface GraphVisualizationProps {
    execution: ExecutionResponse;
}

export default function GraphVisualization({ execution }: GraphVisualizationProps) {
    const { nodes, edges } = useMemo(() => {
        const agentNames = ['planner', 'research', 'validator', 'risk', 'decision'];
        const executedAgents = execution.execution_path || [];

        const nodes: Node[] = agentNames.map((name, index) => {
            const executed = executedAgents.includes(name);
            const isCurrent = executedAgents[executedAgents.length - 1] === name;

            return {
                id: name,
                type: 'default',
                position: { x: index * 200, y: 100 },
                data: {
                    label: (
                        <div className="flex items-center space-x-2">
                            {executed ? (
                                <CheckCircle className="w-4 h-4 text-green-600" />
                            ) : isCurrent ? (
                                <Circle className="w-4 h-4 text-blue-600 animate-pulse" />
                            ) : (
                                <Circle className="w-4 h-4 text-gray-400" />
                            )}
                            <span className={executed ? 'font-medium' : 'text-gray-500'}>
                                {name.charAt(0).toUpperCase() + name.slice(1)}
                            </span>
                        </div>
                    ),
                },
                style: {
                    background: executed ? '#f0fdf4' : '#f9fafb',
                    border: `2px solid ${executed ? '#22c55e' : '#e5e7eb'}`,
                    borderRadius: '8px',
                    padding: '12px',
                },
            };
        });

        const edges: Edge[] = agentNames.slice(0, -1).map((name, index) => ({
            id: `${name}-${agentNames[index + 1]}`,
            source: name,
            target: agentNames[index + 1],
            animated: executedAgents.includes(name) && executedAgents.includes(agentNames[index + 1]),
            style: {
                stroke: executedAgents.includes(agentNames[index + 1]) ? '#22c55e' : '#e5e7eb',
            },
        }));

        return { nodes, edges };
    }, [execution.execution_path]);

    return (
        <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Agent Execution Flow
            </h3>

            <div className="h-[300px] bg-gray-50 rounded-lg border border-gray-200 relative">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    fitView
                    attributionPosition="bottom-left"
                    proOptions={{ hideAttribution: true }}
                >
                    <Background />
                    <Controls />
                    <MiniMap
                        nodeColor={(node) => {
                            const executedAgents = execution.execution_path || [];
                            return executedAgents.includes(node.id) ? '#22c55e' : '#d1d5db';
                        }}
                        nodeStrokeWidth={3}
                        nodeBorderRadius={4}
                        maskColor="rgba(100, 100, 100, 0.2)"
                        style={{
                            backgroundColor: '#ffffff',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                        }}
                        zoomable
                        pannable
                    />
                </ReactFlow>
            </div>

            <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="flex items-center space-x-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-gray-700">Completed</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                    <Circle className="w-4 h-4 text-blue-600" />
                    <span className="text-gray-700">In Progress</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                    <Circle className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-700">Pending</span>
                </div>
            </div>
        </div>
    );
}
