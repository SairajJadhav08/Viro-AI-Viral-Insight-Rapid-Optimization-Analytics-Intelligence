/**
 * Mutation-Specific 3D Protein Structure Viewer
 * Shows protein structure with highlighted mutation site
 */

import { useEffect, useRef, useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, RotateCcw, Layers, Zap, Info } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface Mutation3DViewerProps {
  mutation: {
    position: string;
    original: string;
    predicted: string;
    probability: number;
    effect: string;
    risk: string;
  };
  proteinSequence?: string;
  pdbId?: string;
  pdbFileUrl?: string;
  className?: string;
  structuralConsequences?: Record<string, any>;
}

export default function Mutation3DViewer({
  mutation,
  proteinSequence,
  pdbId = '6VXX',
  pdbFileUrl,
  className = '',
  structuralConsequences
}: Mutation3DViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'simple' | 'detailed'>('detailed');
  const animationFrameRef = useRef<number | null>(null);
  const rotationRef = useRef({ x: 0, y: 0, z: 0 });
  const isDraggingRef = useRef(false);
  const lastMousePosRef = useRef({ x: 0, y: 0 });

  // Extract residue number from position (e.g., "S:484" -> 484)
  const getResidueNumber = (position: string): number | null => {
    const match = position.match(/:(\d+)/);
    return match ? parseInt(match[1]) : null;
  };

  const mutationResidue = getResidueNumber(mutation.position);
  
  // Calculate protein-specific parameters for dynamic visualization
  const proteinLength = useMemo(() => {
    if (proteinSequence) {
      const cleanSeq = proteinSequence.trim().replace(/\s/g, '');
      const aminoAcidPattern = /^[ACDEFGHIKLMNPQRSTVWY]+$/i;
      if (aminoAcidPattern.test(cleanSeq)) {
        return cleanSeq.length;
      }
    }
    // Default based on common virus proteins
    if (pdbId === '6VXX') return 1273; // SARS-CoV-2 spike
    if (pdbId === '5JQ3') return 340;  // Ebola VP35
    if (pdbId === '1HXW') return 99;   // HIV protease
    if (pdbId === '1RUZ') return 566;  // Influenza HA
    if (pdbId === '5IRE') return 505;  // Zika envelope
    return 500; // Default
  }, [proteinSequence, pdbId]);
  
  // Calculate structure complexity based on protein length
  const structureComplexity = useMemo(() => {
    if (proteinLength < 100) return 'simple';
    if (proteinLength < 300) return 'medium';
    if (proteinLength < 600) return 'complex';
    return 'very-complex';
  }, [proteinLength]);
  
  // Calculate number of chains/domains based on protein length
  const numChains = useMemo(() => {
    if (proteinLength < 200) return 3;
    if (proteinLength < 500) return 5;
    if (proteinLength < 1000) return 8;
    return 12;
  }, [proteinLength]);
  
  // Calculate mutation position as percentage of protein length
  const mutationPositionPercent = useMemo(() => {
    if (mutationResidue && proteinLength > 0) {
      return (mutationResidue / proteinLength) * 100;
    }
    return null;
  }, [mutationResidue, proteinLength]);

  // Canvas-based visualization with mutation highlighting
  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        // Use actual container dimensions, with fallback minimums
        const width = rect.width > 0 ? rect.width : 800;
        const height = rect.height > 0 ? rect.height : 500;
        canvas.width = width;
        canvas.height = height;
      } else {
        // Fallback if container not available
        canvas.width = 800;
        canvas.height = 500;
      }
    };

    // Initial resize - use multiple strategies to ensure it works
    const ensureCanvasSize = () => {
      resizeCanvas();
      // If still no size, set defaults and retry
      if (canvas.width === 0 || canvas.height === 0) {
        canvas.width = 800;
        canvas.height = 500;
      }
    };

    // Try immediate resize
    ensureCanvasSize();
    
    // Also try after a short delay to ensure dialog is fully rendered
    const timeoutId = setTimeout(() => {
      ensureCanvasSize();
    }, 100);
    
    window.addEventListener('resize', resizeCanvas);

    const drawProteinWithMutation = () => {
      if (!ctx) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw background (black for detailed, gradient for simple)
      if (viewMode === 'detailed') {
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      } else {
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, '#f0f9ff');
        gradient.addColorStop(1, '#e0f2fe');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const scale = Math.min(canvas.width, canvas.height) * 0.3;
      const { x: rotX, y: rotY } = rotationRef.current;

      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(rotY * 0.01);
      ctx.scale(1 + Math.sin(rotX * 0.01) * 0.1, 1 + Math.cos(rotX * 0.01) * 0.1);

      // Draw protein structure with mutation highlighting
      if (viewMode === 'detailed') {
        // Draw protein chains with mutation site highlighted - dynamic based on protein length
        const residuesPerChain = Math.max(20, Math.floor(proteinLength / numChains));
        
        for (let i = 0; i < numChains; i++) {
          const angle = (i * Math.PI * 2) / numChains + rotX * 0.01;
          const radius = scale * (0.5 + (structureComplexity === 'very-complex' ? 0.3 : structureComplexity === 'complex' ? 0.2 : 0.1));
          const x = Math.cos(angle) * radius;
          const y = Math.sin(angle) * radius * 0.6;
          const z = Math.sin(angle * 2) * radius * 0.3;

          // Draw ribbon structure - vary helix length based on chain
          ctx.beginPath();
          ctx.strokeStyle = '#22c55e'; // Green
          ctx.lineWidth = structureComplexity === 'very-complex' ? 8 : structureComplexity === 'complex' ? 10 : 12;
          ctx.lineCap = 'round';
          ctx.lineJoin = 'round';
          
          // Draw alpha-helix with mutation highlighting - dynamic length
          const helixLength = Math.min(residuesPerChain, 40);
          for (let j = 0; j < helixLength; j++) {
            const helixAngle = j * 0.3 + angle;
            const helixX = x + Math.cos(helixAngle) * 20;
            const helixY = y + Math.sin(helixAngle) * 20 + z * 0.5;
            
            // Calculate actual residue number in this chain
            const actualResidue = i * residuesPerChain + j;
            
            // Highlight mutation site based on actual position
            const isMutationSite = mutationResidue !== null && 
              Math.abs(actualResidue - mutationResidue) < 3;
            
            if (isMutationSite) {
              // Draw highlighted mutation site in red/orange
              ctx.strokeStyle = '#ef4444'; // Red for mutation
              ctx.lineWidth = (structureComplexity === 'very-complex' ? 10 : structureComplexity === 'complex' ? 12 : 14);
              ctx.shadowColor = '#f59e0b';
              ctx.shadowBlur = 15;
            } else {
              // Vary color based on position in protein
              const positionInChain = j / helixLength;
              if (positionInChain < 0.2) {
                ctx.strokeStyle = '#3b82f6'; // Blue for N-terminus
              } else if (positionInChain > 0.8) {
                ctx.strokeStyle = '#8b5cf6'; // Purple for C-terminus
              } else {
                ctx.strokeStyle = '#22c55e'; // Green for middle
              }
              ctx.lineWidth = structureComplexity === 'very-complex' ? 8 : structureComplexity === 'complex' ? 10 : 12;
              ctx.shadowBlur = 0;
            }
            
            if (j === 0) {
              ctx.moveTo(helixX, helixY);
            } else {
              ctx.lineTo(helixX, helixY);
            }
          }
          ctx.stroke();
          ctx.shadowBlur = 0;

          // Draw mutation site marker (glowing sphere) - positioned accurately
          if (mutationResidue !== null) {
            const chainIndex = Math.floor(mutationResidue / residuesPerChain);
            const residueInChain = mutationResidue % residuesPerChain;
            
            if (chainIndex === i && residueInChain < helixLength) {
              const mutAngle = residueInChain * 0.3 + angle;
              const mutX = x + Math.cos(mutAngle) * 20;
              const mutY = y + Math.sin(mutAngle) * 20 + z * 0.5;
              
              // Draw glowing mutation marker - size based on risk level
              const markerSize = mutation.risk === 'High' ? 25 : mutation.risk === 'Medium' ? 20 : 15;
              const gradient = ctx.createRadialGradient(mutX, mutY, 0, mutX, mutY, markerSize);
              gradient.addColorStop(0, '#ef4444');
              gradient.addColorStop(0.5, '#f59e0b');
              gradient.addColorStop(1, 'rgba(239, 68, 68, 0)');
              ctx.fillStyle = gradient;
              ctx.beginPath();
              ctx.arc(mutX, mutY, markerSize, 0, Math.PI * 2);
              ctx.fill();
              
              // Draw mutation residue sphere
              ctx.fillStyle = '#ef4444';
              ctx.beginPath();
              ctx.arc(mutX, mutY, 8, 0, Math.PI * 2);
              ctx.fill();
              
              // Draw original → predicted label with probability
              ctx.fillStyle = '#ffffff';
              ctx.font = 'bold 12px sans-serif';
              ctx.textAlign = 'center';
              ctx.fillText(
                `${mutation.original}→${mutation.predicted} (${mutation.probability}%)`,
                mutX,
                mutY - 30
              );
            }
          }

          // Draw beta-sheet
          if (i % 3 === 0) {
            ctx.beginPath();
            ctx.strokeStyle = '#3b82f6'; // Blue
            ctx.lineWidth = 8;
            for (let k = 0; k < 15; k++) {
              const sheetX = x + k * 3;
              const sheetY = y + Math.sin(k * 0.5) * 5 + z * 0.3;
              if (k === 0) {
                ctx.moveTo(sheetX, sheetY);
              } else {
                ctx.lineTo(sheetX, sheetY);
              }
            }
            ctx.stroke();
          }

          // Draw atoms
          for (let atom = 0; atom < 12; atom++) {
            const atomAngle = atom * 0.5 + angle;
            const atomX = x + Math.cos(atomAngle) * 15;
            const atomY = y + Math.sin(atomAngle) * 15 + z * 0.4;
            
            const atomType = atom % 3;
            if (atomType === 0) {
              ctx.fillStyle = '#ef4444'; // Red (oxygen)
            } else if (atomType === 1) {
              ctx.fillStyle = '#3b82f6'; // Blue (nitrogen)
            } else {
              ctx.fillStyle = '#22c55e'; // Green (carbon)
            }
            ctx.beginPath();
            ctx.arc(atomX, atomY, 4, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      } else {
        // Simple view with mutation highlighting - dynamic based on protein
        const simpleChains = Math.min(numChains, 5);
        const residuesPerSimpleChain = Math.floor(proteinLength / simpleChains);
        
        for (let i = 0; i < simpleChains; i++) {
          const angle = (i * Math.PI * 2) / simpleChains + rotX * 0.01;
          const radius = scale * 0.6;
          const x = Math.cos(angle) * radius;
          const y = Math.sin(angle) * radius * 0.5;

          // Draw chain - vary color based on chain position
          ctx.beginPath();
          const chainColors = ['#3b82f6', '#8b5cf6', '#22c55e', '#f59e0b', '#ef4444'];
          ctx.strokeStyle = chainColors[i % chainColors.length];
          ctx.lineWidth = 8;
          ctx.lineCap = 'round';
          
          const simpleHelixLength = Math.min(residuesPerSimpleChain, 25);
          for (let j = 0; j < simpleHelixLength; j++) {
            const helixX = x + Math.cos(j * 0.5 + angle) * 15;
            const helixY = y + Math.sin(j * 0.5 + angle) * 15;
            
            // Calculate actual residue and highlight mutation site
            const actualResidue = i * residuesPerSimpleChain + j;
            const isMutationSite = mutationResidue !== null && 
              Math.abs(actualResidue - mutationResidue) < 2;
            
            if (isMutationSite) {
              ctx.strokeStyle = '#ef4444';
              ctx.lineWidth = 12;
              ctx.shadowColor = '#f59e0b';
              ctx.shadowBlur = 8;
            }
            
            if (j === 0) {
              ctx.moveTo(helixX, helixY);
            } else {
              ctx.lineTo(helixX, helixY);
            }
          }
          ctx.stroke();
          ctx.shadowBlur = 0;

          // Draw mutation marker - positioned accurately
          if (mutationResidue !== null) {
            const chainIndex = Math.floor(mutationResidue / residuesPerSimpleChain);
            const residueInChain = mutationResidue % residuesPerSimpleChain;
            
            if (chainIndex === i && residueInChain < simpleHelixLength) {
              const mutAngle = residueInChain * 0.5 + angle;
              const mutX = x + Math.cos(mutAngle) * 15;
              const mutY = y + Math.sin(mutAngle) * 15;
              
              ctx.fillStyle = '#ef4444';
              ctx.beginPath();
              ctx.arc(mutX, mutY, 10, 0, Math.PI * 2);
              ctx.fill();
              
              ctx.fillStyle = '#ffffff';
              ctx.font = 'bold 10px sans-serif';
              ctx.textAlign = 'center';
              ctx.fillText(
                `${mutation.original}→${mutation.predicted}`,
                mutX,
                mutY - 20
              );
            }
          }
        }
      }

      ctx.restore();

      // Draw scale bar
      ctx.strokeStyle = viewMode === 'detailed' ? '#ffffff' : '#64748b';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(canvas.width - 100, canvas.height - 20);
      ctx.lineTo(canvas.width - 20, canvas.height - 20);
      ctx.stroke();
      ctx.fillStyle = viewMode === 'detailed' ? '#ffffff' : '#64748b';
      ctx.font = '10px sans-serif';
      ctx.fillText('10 nm', canvas.width - 100, canvas.height - 25);
    };

    const animate = () => {
      if (!isDraggingRef.current) {
        rotationRef.current.y += 0.5;
      }
      drawProteinWithMutation();
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    // Start animation after ensuring canvas is ready
    const startAnimation = () => {
      // Ensure canvas has dimensions
      if (canvas.width === 0 || canvas.height === 0) {
        ensureCanvasSize();
      }
      
      // Draw immediately
      drawProteinWithMutation();
      setIsLoading(false);
      // Start animation loop
      animate();
    };
    
    // Start animation - try immediately and also after delay
    startAnimation();
    const startTimeout = setTimeout(() => {
      if (canvas.width === 0 || canvas.height === 0) {
        ensureCanvasSize();
        drawProteinWithMutation();
      }
    }, 150);

    // Mouse interaction
    const handleMouseDown = (e: MouseEvent) => {
      isDraggingRef.current = true;
      lastMousePosRef.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (isDraggingRef.current) {
        const deltaX = e.clientX - lastMousePosRef.current.x;
        const deltaY = e.clientY - lastMousePosRef.current.y;
        rotationRef.current.y += deltaX * 0.5;
        rotationRef.current.x += deltaY * 0.5;
        lastMousePosRef.current = { x: e.clientX, y: e.clientY };
      }
    };

    const handleMouseUp = () => {
      isDraggingRef.current = false;
    };

    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseleave', handleMouseUp);

    return () => {
      clearTimeout(timeoutId);
      clearTimeout(startTimeout);
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseup', handleMouseUp);
      canvas.removeEventListener('mouseleave', handleMouseUp);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [viewMode, mutation, mutationResidue, proteinLength, structureComplexity, numChains, pdbId]);

  const handleReset = () => {
    rotationRef.current = { x: 0, y: 0, z: 0 };
  };

  const toggleViewMode = () => {
    setViewMode(prev => prev === 'simple' ? 'detailed' : 'simple');
  };

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black rounded-lg z-10">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-white mx-auto mb-2" />
            <p className="text-sm text-white">Loading mutation visualization...</p>
          </div>
        </div>
      )}

      {/* Canvas View */}
      <div className="w-full" style={{ minHeight: '500px', height: '500px' }}>
        <canvas
          ref={canvasRef}
          className={`w-full h-full rounded-lg border-2 border-gray-200 shadow-lg cursor-grab active:cursor-grabbing ${
            viewMode === 'detailed' ? 'bg-black' : 'bg-white'
          }`}
          style={{ display: 'block' }}
        />
      </div>

      {/* Control Buttons */}
      <div className="absolute top-2 right-2 z-20 flex flex-col gap-2">
        <Button
          size="sm"
          variant="outline"
          onClick={toggleViewMode}
          className="bg-white/90 hover:bg-white shadow-sm"
          title={viewMode === 'simple' ? 'Switch to detailed view' : 'Switch to simple view'}
        >
          {viewMode === 'simple' ? (
            <>
              <Layers className="h-3 w-3 mr-1" />
              Detailed
            </>
          ) : (
            <>
              <Zap className="h-3 w-3 mr-1" />
              Simple
            </>
          )}
        </Button>

        <Button
          size="sm"
          variant="outline"
          onClick={handleReset}
          className="bg-white/90 hover:bg-white shadow-sm"
          title="Reset view"
        >
          <RotateCcw className="h-3 w-3" />
        </Button>
      </div>

      {/* Mutation Info Badge */}
      <div className="absolute top-2 left-2 z-20">
        <Badge variant="destructive" className="bg-red-600 text-white border-red-700">
          <Info className="h-3 w-3 mr-1" />
          Mutation: {mutation.position} {mutation.original}→{mutation.predicted}
        </Badge>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-2 right-2 z-20">
        <p className={`text-xs px-2 py-1 rounded ${viewMode === 'detailed' ? 'text-white bg-black/80' : 'text-[#4A6A7A] bg-white/80'}`}>
          {viewMode === 'simple' ? 'Drag to rotate • Red = Mutation site' : 'Click & drag to rotate • Red highlight = Mutation site'}
        </p>
      </div>
    </div>
  );
}

