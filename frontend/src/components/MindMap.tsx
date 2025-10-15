/**
 * Mind map visualization component using React Flow
 */
import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'react-flow-renderer';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { KeywordRelations } from '../types';

interface MindMapProps {
  data: KeywordRelations;
}

export function MindMap({ data }: MindMapProps) {
  // Convert API data to React Flow format
  const initialNodes: Node[] = useMemo(() => {
    return data.nodes.map((node, index) => {
      const isCentral = node.type === 'central';
      const angle = (index / data.nodes.length) * 2 * Math.PI;
      const radius = isCentral ? 0 : 250;

      return {
        id: node.id,
        data: {
          label: node.label,
        },
        position: {
          x: isCentral ? 400 : 400 + radius * Math.cos(angle),
          y: isCentral ? 300 : 300 + radius * Math.sin(angle),
        },
        style: {
          background: isCentral ? '#3b82f6' : '#10b981',
          color: 'white',
          border: '2px solid #fff',
          borderRadius: '50%',
          width: isCentral ? 120 : 80,
          height: isCentral ? 120 : 80,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '10px',
          fontSize: isCentral ? '14px' : '12px',
          fontWeight: isCentral ? 'bold' : 'normal',
          textAlign: 'center',
        },
      };
    });
  }, [data.nodes]);

  const initialEdges: Edge[] = useMemo(() => {
    return data.edges.map((edge) => ({
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      label: edge.relationship_type,
      type: 'smoothstep',
      animated: edge.strength > 0.7,
      style: {
        stroke: edge.strength > 0.7 ? '#3b82f6' : '#94a3b8',
        strokeWidth: edge.strength * 3,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: edge.strength > 0.7 ? '#3b82f6' : '#94a3b8',
      },
      labelStyle: {
        fill: '#64748b',
        fontSize: 10,
      },
      labelBgStyle: {
        fill: '#fff',
        fillOpacity: 0.8,
      },
    }));
  }, [data.edges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Keyword Relationship Map</CardTitle>
        <p className="text-sm text-gray-600">
          {data.total_relations} relationships found
        </p>
      </CardHeader>
      <CardContent>
        <div className="h-[600px] border rounded-lg bg-gray-50">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            attributionPosition="bottom-left"
          >
            <Background />
            <Controls />
          </ReactFlow>
        </div>
        <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500"></div>
            <span>Central Keyword</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>Related Keywords</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-blue-500"></div>
            <span>Strong Connection</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-gray-400"></div>
            <span>Weak Connection</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
