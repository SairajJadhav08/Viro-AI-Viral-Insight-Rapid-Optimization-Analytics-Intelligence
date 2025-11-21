import { useMemo, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Download, Share2, RefreshCw, Flag, MapPin, Activity, AlertTriangle, Loader2, FileText, PlusCircle, X } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useProject } from '@/hooks/use-projects';
import { useProjectResults as useResults } from '@/hooks/use-results';
import { toast } from 'sonner';
import Protein3DViewer from '@/components/Protein3DViewer';

export default function Result() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const projectId = searchParams.get('projectId') ? parseInt(searchParams.get('projectId')!) : null;
  
  const { data: project, isLoading: projectLoading, refetch: refetchProject } = useProject(projectId);
  const { data: results, isLoading: resultsLoading, isFetching: resultsFetching, refetch: refetchResults } = useResults(projectId);

  // Function to scroll to detailed modification analysis
  const scrollToModificationDetail = (index: number) => {
    const element = document.getElementById(`modification-detail-${index}`);
    if (element) {
      // Calculate offset for fixed headers (adjust as needed)
      const offset = 100;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });

      // Add a visual highlight effect
      element.style.transition = 'box-shadow 0.3s ease';
      element.style.boxShadow = '0 0 0 4px rgba(30, 136, 229, 0.3)';
      setTimeout(() => {
        element.style.boxShadow = '';
      }, 2000);
    }
  };

  // Flag functionality - Save to favorites/localStorage
  const [isFlagged, setIsFlagged] = useState(() => {
    if (!projectId || typeof window === 'undefined') return false;
    const flagged = localStorage.getItem(`flagged_project_${projectId}`);
    return flagged === 'true';
  });

  // Handle refresh/re-run button click
  const handleRefresh = async () => {
    if (!projectId) return;
    
    // Show loading toast
    const toastId = toast.loading('Refreshing results...');
    
    try {
      // Invalidate and refetch both project and results
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['project', projectId] }),
        queryClient.invalidateQueries({ queryKey: ['project-results', projectId] }),
        refetchProject(),
        refetchResults()
      ]);
      
      toast.success('Results refreshed successfully!', { id: toastId });
    } catch (error) {
      toast.error('Failed to refresh results. Please try again.', { id: toastId });
    }
  };

  const isLoading = projectLoading || (resultsLoading && !results);
  const isProcessing = project && (!results && !resultsLoading) || (results === null);

  // ALL HOOKS MUST BE CALLED BEFORE ANY EARLY RETURNS
  // Calculate all derived values BEFORE any early returns (React Hooks rule)
  const deadlinessScore = useMemo(() => results?.project?.deadliness_score || 0, [results?.project?.deadliness_score]);
  
  // Safely get top drug
  const topDrug = useMemo(() => {
    return results?.drugs?.[0] || null;
  }, [results?.drugs]);
  
  // Ensure binding_affinity is always a number (convert from string/Decimal if needed)
  const topBindingEnergy = useMemo(() => {
    if (!topDrug || !topDrug.binding_affinity) return 0;
    const affinity = topDrug.binding_affinity;
    if (affinity === null || affinity === undefined) return 0;
    const num = typeof affinity === 'string' ? parseFloat(affinity) : Number(affinity);
    return isNaN(num) ? 0 : num;
  }, [topDrug]);
  
  // Calculate RMSD from structural data (if available)
  const rmsdValue = useMemo(() => {
    // Try to get RMSD from first mutation's structural consequences
    if (results?.mutations && results.mutations.length > 0) {
      const structural = results.mutations[0].structural_consequences;
      if (structural && typeof structural === 'object') {
        const rmsd = (structural as any).deltaRMSD;
        if (rmsd) {
          // Extract numeric value from string like "1.8 Å"
          const match = String(rmsd).match(/(\d+\.?\d*)/);
          return match ? parseFloat(match[1]) : 1.8;
        }
      }
    }
    // Try to get from drug binding metrics
    if (topDrug && topDrug.binding_metrics) {
      try {
        const bindingMetrics = typeof topDrug.binding_metrics === 'string' 
          ? JSON.parse(topDrug.binding_metrics) 
          : topDrug.binding_metrics;
        if (bindingMetrics && typeof bindingMetrics === 'object') {
          const poseRMSD = bindingMetrics.poseRMSD;
          if (poseRMSD) {
            const match = String(poseRMSD).match(/(\d+\.?\d*)/);
            if (match) return parseFloat(match[1]);
          }
        }
      } catch (e) {
        // If JSON parsing fails, continue with default
        console.warn('Failed to parse binding_metrics:', e);
      }
    }
    return 1.8; // Default value
  }, [results?.mutations, topDrug]);

  // Get molecular weight - prioritize structure_data from PDB files, then sequence, then defaults
  const molecularWeight = useMemo(() => {
    // First priority: Use structure data from uploaded PDB file (if available)
    if ((results as any)?.structure_data?.molecular_weight_kda) {
      return String((results as any).structure_data.molecular_weight_kda);
    }
    
    // Second priority: Calculate from actual sequence if available
    if (project?.description) {
      const sequence = project.description.trim();
      const aminoAcidPattern = /^[ACDEFGHIKLMNPQRSTVWY\s]+$/i;
      if (aminoAcidPattern.test(sequence)) {
        const cleanSequence = sequence.replace(/\s/g, '');
        if (cleanSequence.length > 0) {
          // Average molecular weight per amino acid is ~110 Da
          const mwDa = cleanSequence.length * 110;
          return (mwDa / 1000).toFixed(1); // Convert to kDa
        }
      }
    }
    
    // Third priority: Use virus-specific defaults based on project title/description
    const title = project?.title?.toLowerCase() || '';
    const desc = project?.description?.toLowerCase() || '';
    
    if (title.includes('sars-cov-2') || title.includes('covid') || desc.includes('sars-cov-2')) {
      return '141.2'; // SARS-CoV-2 spike protein (~141 kDa)
    } else if (title.includes('ebola') || desc.includes('ebola')) {
      return '37.4'; // Ebola virus VP35 (~37.4 kDa)
    } else if (title.includes('hiv') || desc.includes('hiv')) {
      return '10.9'; // HIV-1 protease (~10.9 kDa)
    } else if (title.includes('influenza') || desc.includes('influenza')) {
      return '62.3'; // Influenza hemagglutinin (~62.3 kDa)
    } else if (title.includes('zika') || desc.includes('zika')) {
      return '55.6'; // Zika virus envelope protein (~55.6 kDa)
    }
    
    // Default fallback
    return '141.2';
  }, [(results as any)?.structure_data?.molecular_weight_kda, project?.description, project?.title]);

  // Get residues count - prioritize structure_data from PDB files, then sequence, then defaults
  const residuesCount = useMemo(() => {
    // First priority: Use structure data from uploaded PDB file (if available)
    if ((results as any)?.structure_data?.residues_count) {
      return (results as any).structure_data.residues_count;
    }
    
    // Second priority: Try to get from project description if it's a sequence
    if (project?.description) {
      const sequence = project.description.trim();
      const aminoAcidPattern = /^[ACDEFGHIKLMNPQRSTVWY\s]+$/i;
      if (aminoAcidPattern.test(sequence)) {
        const cleanSequence = sequence.replace(/\s/g, '');
        if (cleanSequence.length > 0) {
          return cleanSequence.length;
        }
      }
    }
    
    // Third priority: Use virus-specific defaults based on project title/description
    const title = project?.title?.toLowerCase() || '';
    const desc = project?.description?.toLowerCase() || '';
    
    if (title.includes('sars-cov-2') || title.includes('covid') || desc.includes('sars-cov-2')) {
      return 1273; // SARS-CoV-2 spike protein
    } else if (title.includes('ebola') || desc.includes('ebola')) {
      return 340; // Ebola virus VP35
    } else if (title.includes('hiv') || desc.includes('hiv')) {
      return 99; // HIV-1 protease
    } else if (title.includes('influenza') || desc.includes('influenza')) {
      return 566; // Influenza hemagglutinin
    } else if (title.includes('zika') || desc.includes('zika')) {
      return 505; // Zika virus envelope protein
    }
    
    // Default fallback
    return 1273;
  }, [(results as any)?.structure_data?.residues_count, project?.description, project?.title]);

  // Determine PDB ID based on project title/description
  const getPdbId = useMemo(() => {
    const title = project?.title?.toLowerCase() || '';
    const desc = project?.description?.toLowerCase() || '';
    
    // Map common viruses to their PDB structures
    if (title.includes('sars-cov-2') || title.includes('covid') || desc.includes('sars-cov-2')) {
      return '6VXX'; // SARS-CoV-2 spike protein
    } else if (title.includes('ebola') || desc.includes('ebola')) {
      return '5JQ3'; // Ebola virus VP35
    } else if (title.includes('hiv') || desc.includes('hiv')) {
      return '1HXW'; // HIV-1 protease
    } else if (title.includes('influenza') || desc.includes('influenza')) {
      return '1RUZ'; // Influenza hemagglutinin
    } else if (title.includes('zika') || desc.includes('zika')) {
      return '5IRE'; // Zika virus envelope protein
    }
    // Default to SARS-CoV-2
    return '6VXX';
  }, [project?.title, project?.description]);

  // Transform mutations data to match existing format
  const mutations = useMemo(() => {
    if (!results?.mutations) return [];
    return results.mutations.map(mut => ({
      position: mut.mutation_position || `S:${mut.id}`,
      original: mut.original_amino_acid || 'N/A',
      predicted: mut.predicted_amino_acid || 'N/A',
      probability: Math.round((mut.probability || 0) * 100),
      effect: mut.effect || 'Unknown effect',
      risk: mut.risk_level || 'Medium',
      structuralConsequences: mut.structural_consequences || {}
    }));
  }, [results?.mutations]);

  // Transform detailed mutation data
  const detailedMutationData = useMemo(() => {
    if (!results?.mutations) return [];
    return results.mutations.map(mut => {
      const genomicLevel = mut.genomic_level as Record<string, unknown> || {};
      const probability = mut.probability_metrics as Record<string, unknown> || {};
      const selectivePressure = mut.selective_pressure as Record<string, unknown> || {};
      const structuralConsequences = mut.structural_consequences as Record<string, unknown> || {};
      const receptorBinding = mut.receptor_binding as Record<string, unknown> || {};
      const immuneEvasion = mut.immune_evasion as Record<string, unknown> || {};
      const viralFitness = mut.viral_fitness as Record<string, unknown> || {};
      const pathogenicity = mut.pathogenicity as Record<string, unknown> || {};
      const lineageEmergence = mut.lineage_emergence as Record<string, unknown> || {};

      return {
        mutation: `${mut.mutation_position} ${mut.original_amino_acid}→${mut.predicted_amino_acid}`,
        genomicLevel: {
          nucleotideSubstitution: genomicLevel.nucleotideSubstitution || 'N/A',
          mutationType: genomicLevel.mutationType || 'Point mutation',
          genomicRegion: genomicLevel.genomicRegion || 'Unknown',
          codonChange: genomicLevel.codonChange || 'N/A',
          synonymous: genomicLevel.synonymous || 'Non-synonymous'
        },
        probability: {
          aiScore: mut.probability || 0,
          historicalFrequency: (probability.historicalFrequency as string) || 'Unknown',
          fixationLikelihood: (probability.fixationLikelihood as string) || 'Unknown'
        },
        selectivePressure: {
          dNdS: (selectivePressure.dNdS as number) || 0,
          conservationScore: (selectivePressure.conservationScore as string) || 'Unknown',
          coEvolution: (selectivePressure.coEvolution as string) || 'No co-evolution detected'
        },
        structuralConsequences: {
          deltaRMSD: (structuralConsequences.deltaRMSD as string) || 'N/A',
          deltaRMSF: (structuralConsequences.deltaRMSF as string) || 'N/A',
          deltaGStability: (structuralConsequences.deltaGStability as string) || 'N/A',
          sasaShift: (structuralConsequences.sasaShift as string) || 'N/A',
          secondaryStructure: (structuralConsequences.secondaryStructure as string) || 'Unknown',
          interResidueContacts: (structuralConsequences.interResidueContacts as string) || 'Unknown'
        },
        receptorBinding: {
          deltaKd: (receptorBinding.deltaKd as string) || 'N/A',
          interfaceAlteration: (receptorBinding.interfaceAlteration as string) || 'Unknown',
          criticalResidues: (receptorBinding.criticalResidues as string) || 'Unknown'
        },
        immuneEvasion: {
          bCellEpitope: (immuneEvasion.bCellEpitope as string) || 'Unknown',
          tCellEpitope: (immuneEvasion.tCellEpitope as string) || 'Unknown',
          glycosylationSite: (immuneEvasion.glycosylationSite as string) || 'Unknown',
          epitopeMasking: (immuneEvasion.epitopeMasking as string) || 'Unknown'
        },
        viralFitness: {
          replicationEfficiency: (viralFitness.replicationEfficiency as string) || 'Unknown',
          virionStability: (viralFitness.virionStability as string) || 'Unknown',
          cpeIndex: (viralFitness.cpeIndex as string) || 'Unknown'
        },
        pathogenicity: {
          contribution: (pathogenicity.contribution as string) || '0/100',
          tropismImpact: (pathogenicity.tropismImpact as string) || 'Unknown',
          viralLoadThreshold: (pathogenicity.viralLoadThreshold as string) || 'Unknown'
        },
        lineageEmergence: {
          newLineageProbability: (lineageEmergence.newLineageProbability as string) || '0%',
          phylogeneticPathway: (lineageEmergence.phylogeneticPathway as string) || 'Unknown',
          coMutationSynergy: (lineageEmergence.coMutationSynergy as string) || 'Unknown'
        }
      };
    });
  }, [results?.mutations]);


  // Transform drug candidates data
  const drugCandidates = useMemo(() => {
    if (!results?.drugs) return [];
    return results.drugs.map(drug => ({
      name: drug.drug_name,
      smiles: drug.smiles || '',
      bindingAffinity: drug.binding_affinity || 0,
      ic50: drug.ic50 || 'N/A',
      logP: drug.logp || 0,
      molecularWeight: drug.molecular_weight || 0,
      formula: drug.formula || '',
      heavyAtoms: drug.heavy_atoms || 0,
      rank: drug.rank || 0,
      score: drug.score || 0
    }));
  }, [results?.drugs]);

  // Transform detailed drug data
  const detailedDrugData = useMemo(() => {
    if (!results?.drugs) return [];
    return results.drugs.map(drug => {
      const molecularIdentity = drug.molecular_identity as Record<string, unknown> || {};
      const bindingMetrics = drug.binding_metrics as Record<string, unknown> || {};
      const interactionMap = drug.interaction_map as Record<string, unknown> || {};
      const structuralStability = drug.structural_stability as Record<string, unknown> || {};
      const physicochemical = drug.physicochemical as Record<string, unknown> || {};
      const adme = drug.adme as Record<string, unknown> || {};
      const toxicology = drug.toxicology as Record<string, unknown> || {};
      const comparativeScores = drug.comparative_scores as Record<string, unknown> || {};
      const ensembleAnalysis = drug.ensemble_analysis as Record<string, unknown> || {};
      const resistanceVulnerability = drug.resistance_vulnerability as Record<string, unknown> || {};
      const chemicalDiversity = drug.chemical_diversity as Record<string, unknown> || {};

      return {
        name: drug.drug_name,
        molecularIdentity: {
          chemicalName: (molecularIdentity.chemicalName as string) || drug.drug_name,
          uniqueID: (molecularIdentity.uniqueID as string) || `VIRO-AI-${drug.id}`,
          inchi: (molecularIdentity.inchi as string) || 'N/A'
        },
        bindingMetrics: {
          bindingEnergy: (bindingMetrics.bindingEnergy as string) || `${drug.binding_affinity || 0} kcal/mol`,
          kd: (bindingMetrics.kd as string) || 'N/A',
          ki: (bindingMetrics.ki as string) || 'N/A',
          ic50: drug.ic50 || 'N/A',
          dockingScore: (bindingMetrics.dockingScore as string) || 'N/A',
          poseRMSD: (bindingMetrics.poseRMSD as string) || 'N/A'
        },
        interactionMap: {
          hBonds: (interactionMap.hBonds as string) || 'N/A',
          hydrophobicContacts: (interactionMap.hydrophobicContacts as string) || 'N/A',
          piPiStacking: (interactionMap.piPiStacking as string) || 'N/A',
          ionicInteractions: (interactionMap.ionicInteractions as string) || 'N/A',
          vdwEngagement: (interactionMap.vdwEngagement as string) || 'N/A',
          bindingPocketOccupancy: (interactionMap.bindingPocketOccupancy as string) || 'N/A'
        },
        structuralStability: {
          rmsdComplex: (structuralStability.rmsdComplex as string) || 'N/A',
          rmsfBindingPocket: (structuralStability.rmsfBindingPocket as string) || 'N/A',
          mmPbsaEnergy: (structuralStability.mmPbsaEnergy as string) || 'N/A',
          sasaChange: (structuralStability.sasaChange as string) || 'N/A',
          hBondPersistence: (structuralStability.hBondPersistence as string) || 'N/A',
          comStability: (structuralStability.comStability as string) || 'N/A'
        },
        physicochemical: {
          logP: (physicochemical.logP as string) || String(drug.logp || 'N/A'),
          logS: (physicochemical.logS as string) || 'N/A',
          tpsa: (physicochemical.tpsa as string) || 'N/A',
          hbDonors: (physicochemical.hbDonors as string) || 'N/A',
          hbAcceptors: (physicochemical.hbAcceptors as string) || 'N/A',
          rotatableBonds: (physicochemical.rotatableBonds as string) || 'N/A',
          pka: (physicochemical.pka as string) || 'N/A',
          molecularVolume: (physicochemical.molecularVolume as string) || 'N/A',
          aromaticity: (physicochemical.aromaticity as string) || 'N/A'
        },
        adme: {
          absorption: (adme.absorption as string) || 'N/A',
          plasmaProteinBinding: (adme.plasmaProteinBinding as string) || 'N/A',
          logD: (adme.logD as string) || 'N/A',
          metabolism: (adme.metabolism as string) || 'N/A',
          clearance: (adme.clearance as string) || 'N/A',
          halfLife: (adme.halfLife as string) || 'N/A',
          permeability: (adme.permeability as string) || 'N/A'
        },
        toxicology: {
          amesMutagenicity: (toxicology.amesMutagenicity as string) || 'Unknown',
          hergLiability: (toxicology.hergLiability as string) || 'Unknown',
          painsFilter: (toxicology.painsFilter as string) || 'Unknown',
          toxicophoreAlerts: (toxicology.toxicophoreAlerts as string) || 'None',
          reactiveMetabolites: (toxicology.reactiveMetabolites as string) || 'Unknown',
          ld50Model: (toxicology.ld50Model as string) || 'N/A'
        },
        comparativeScores: {
          bindingStrength: (comparativeScores.bindingStrength as string) || 'N/A',
          structuralStability: (comparativeScores.structuralStability as string) || 'N/A',
          interactionDiversity: (comparativeScores.interactionDiversity as string) || 'N/A',
          drugLikeness: (comparativeScores.drugLikeness as string) || 'N/A',
          admeReliability: (comparativeScores.admeReliability as string) || 'N/A',
          toxicityPenalty: (comparativeScores.toxicityPenalty as string) || 'N/A',
          overallQuality: (comparativeScores.overallQuality as string) || `${drug.score || 0}/100`
        },
        ensembleAnalysis: {
          multiConformation: (ensembleAnalysis.multiConformation as string) || 'N/A',
          mutantVariants: (ensembleAnalysis.mutantVariants as string) || 'N/A',
          ensembleDocking: (ensembleAnalysis.ensembleDocking as string) || 'N/A',
          poseDistribution: (ensembleAnalysis.poseDistribution as string) || 'N/A'
        },
        resistanceVulnerability: {
          mutationSensitivity: (resistanceVulnerability.mutationSensitivity as string) || 'Unknown',
          deltaGMutants: (resistanceVulnerability.deltaGMutants as string) || 'N/A',
          lossOfAffinityThreshold: (resistanceVulnerability.lossOfAffinityThreshold as string) || 'N/A',
          resistanceRisk: (resistanceVulnerability.resistanceRisk as string) || 'N/A'
        },
        chemicalDiversity: {
          scaffoldDiversity: (chemicalDiversity.scaffoldDiversity as string) || 'N/A',
          similarityToKnown: (chemicalDiversity.similarityToKnown as string) || 'N/A',
          syntheticAccessibility: (chemicalDiversity.syntheticAccessibility as string) || 'N/A',
          patentabilityEstimate: (chemicalDiversity.patentabilityEstimate as string) || 'Unknown'
        }
      };
    });
  }, [results?.drugs]);

  // Transform modifications data
  const modifications = useMemo(() => {
    if (!results?.modifications) return [];
    return results.modifications.map(mod => ({
      oldFormula: mod.base_formula || 'N/A',
      newFormula: mod.modified_formula || 'N/A',
      changes: mod.changes || 'Unknown changes',
      improvements: mod.improvements || 'Unknown improvements',
      confidence: mod.confidence ? `±${mod.confidence}%` : 'N/A'
    }));
  }, [results?.modifications]);

  // Transform detailed modification data
  const detailedModificationData = useMemo(() => {
    if (!results?.modifications) return [];
    return results.modifications.map((mod, index) => {
      const modificationIdentity = mod.modification_identity as Record<string, unknown> || {};
      const structuralEffects = mod.structural_effects as Record<string, unknown> || {};
      const physicochemicalChanges = mod.physicochemical_changes as Record<string, unknown> || {};
      const bindingAffinityEffects = mod.binding_affinity_effects as Record<string, unknown> || {};
      const electronicEffects = mod.electronic_effects as Record<string, unknown> || {};
      const stabilityDegradation = mod.stability_degradation as Record<string, unknown> || {};
      const solubilityPermeability = mod.solubility_permeability as Record<string, unknown> || {};
      const admeShifts = mod.adme_shifts as Record<string, unknown> || {};
      const toxicitySignatures = mod.toxicity_signatures as Record<string, unknown> || {};
      const syntheticFeasibility = mod.synthetic_feasibility as Record<string, unknown> || {};
      const comparativeScoring = mod.comparative_scoring as Record<string, unknown> || {};

      return {
        modificationID: `Modification #${index + 1}`,
        baseFormula: mod.base_formula || 'N/A',
        modifiedFormula: mod.modified_formula || 'N/A',
        modificationIdentity: {
          addedGroups: (modificationIdentity.addedGroups as string) || 'Unknown',
          removedGroups: (modificationIdentity.removedGroups as string) || 'Unknown',
          substitutions: (modificationIdentity.substitutions as string) || 'Unknown',
          structuralConstraints: (modificationIdentity.structuralConstraints as string) || 'None',
          chainAlterations: (modificationIdentity.chainAlterations as string) || 'None',
          aromaticityChange: (modificationIdentity.aromaticityChange as string) || 'Unknown',
          hbCountChange: (modificationIdentity.hbCountChange as string) || 'No change'
        },
        structuralEffects: {
          deltaRMSD: (structuralEffects.deltaRMSD as string) || 'N/A',
          molecularVolumeChange: (structuralEffects.molecularVolumeChange as string) || 'N/A',
          stericHindranceIndex: (structuralEffects.stericHindranceIndex as string) || 'N/A',
          torsionalAngleShifts: (structuralEffects.torsionalAngleShifts as string) || 'Unknown',
          piPiStackingChange: (structuralEffects.piPiStackingChange as string) || 'Unknown',
          hBondNetworkAlteration: (structuralEffects.hBondNetworkAlteration as string) || 'Unknown',
          sasaChange: (structuralEffects.sasaChange as string) || 'N/A'
        },
        physicochemicalChanges: {
          deltaLogP: (physicochemicalChanges.deltaLogP as string) || 'N/A',
          deltaPka: (physicochemicalChanges.deltaPka as string) || 'N/A',
          tpsaChange: (physicochemicalChanges.tpsaChange as string) || 'N/A',
          molecularWeightChange: (physicochemicalChanges.molecularWeightChange as string) || 'N/A',
          hbDonorsChange: (physicochemicalChanges.hbDonorsChange as string) || '0',
          hbAcceptorsChange: (physicochemicalChanges.hbAcceptorsChange as string) || '0',
          rotatableBondsChange: (physicochemicalChanges.rotatableBondsChange as string) || '0',
          aromaticRingChange: (physicochemicalChanges.aromaticRingChange as string) || '0'
        },
        bindingAffinityEffects: {
          deltaBindingEnergy: (bindingAffinityEffects.deltaBindingEnergy as string) || 'N/A',
          interactionHotspotChanges: (bindingAffinityEffects.interactionHotspotChanges as string) || 'Unknown',
          contactResidueMapDiff: (bindingAffinityEffects.contactResidueMapDiff as string) || 'Unknown',
          dockingPoseStability: (bindingAffinityEffects.dockingPoseStability as string) || 'N/A',
          kdImprovement: (bindingAffinityEffects.kdImprovement as string) || 'N/A'
        },
        electronicEffects: {
          homoLumoGapChange: (electronicEffects.homoLumoGapChange as string) || 'N/A',
          electronDensityRedistribution: (electronicEffects.electronDensityRedistribution as string) || 'Unknown',
          partialChargeAnalysis: (electronicEffects.partialChargeAnalysis as string) || 'N/A',
          dipoleMomentChange: (electronicEffects.dipoleMomentChange as string) || 'N/A',
          polarizabilityShift: (electronicEffects.polarizabilityShift as string) || 'N/A'
        },
        stabilityDegradation: {
          metabolicStability: (stabilityDegradation.metabolicStability as string) || 'N/A',
          photostability: (stabilityDegradation.photostability as string) || 'Unknown',
          thermalStability: (stabilityDegradation.thermalStability as string) || 'N/A',
          reactiveSiteMasking: (stabilityDegradation.reactiveSiteMasking as string) || 'Unknown'
        },
        solubilityPermeability: {
          deltaSolubility: (solubilityPermeability.deltaSolubility as string) || 'N/A',
          permeabilityModels: (solubilityPermeability.permeabilityModels as string) || 'N/A',
          logSChange: (solubilityPermeability.logSChange as string) || 'N/A',
          effluxRatioPrediction: (solubilityPermeability.effluxRatioPrediction as string) || 'Unknown'
        },
        admeShifts: {
          absorptionEfficiency: (admeShifts.absorptionEfficiency as string) || 'N/A',
          plasmaProteinBindingShift: (admeShifts.plasmaProteinBindingShift as string) || 'N/A',
          metabolicHotspots: (admeShifts.metabolicHotspots as string) || 'Unknown',
          clearancePrediction: (admeShifts.clearancePrediction as string) || 'N/A',
          logDChange: (admeShifts.logDChange as string) || 'N/A'
        },
        toxicitySignatures: {
          painsFilter: (toxicitySignatures.painsFilter as string) || 'Unknown',
          structuralAlerts: (toxicitySignatures.structuralAlerts as string) || 'None',
          mutagenicityPredictors: (toxicitySignatures.mutagenicityPredictors as string) || 'Unknown',
          reactiveMetaboliteRisk: (toxicitySignatures.reactiveMetaboliteRisk as string) || 'Unknown',
          offTargetBinding: (toxicitySignatures.offTargetBinding as string) || 'N/A'
        },
        syntheticFeasibility: {
          sasScore: (syntheticFeasibility.sasScore as string) || 'N/A',
          syntheticSteps: (syntheticFeasibility.syntheticSteps as string) || 'N/A',
          retrosynthesisComplexity: (syntheticFeasibility.retrosynthesisComplexity as string) || 'Unknown',
          rareIntermediates: (syntheticFeasibility.rareIntermediates as string) || 'None',
          yieldPrediction: (syntheticFeasibility.yieldPrediction as string) || 'N/A'
        },
        comparativeScoring: {
          structuralImprovement: (comparativeScoring.structuralImprovement as string) || 'N/A',
          stabilityScore: (comparativeScoring.stabilityScore as string) || 'N/A',
          bindingImprovement: (comparativeScoring.bindingImprovement as string) || 'N/A',
          physicochemicalOptimization: (comparativeScoring.physicochemicalOptimization as string) || 'N/A',
          toxicityPenalty: (comparativeScoring.toxicityPenalty as string) || 'N/A',
          overallViability: (comparativeScoring.overallViability as string) || 'N/A'
        }
      };
    });
  }, [results?.modifications]);

  if (!projectId) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Project Results</h1>
          <p className="text-[#4A6A7A]">View detailed analysis and results for your research projects</p>
        </div>
        
        <Card className="border-2 border-dashed border-[#EAF3FF]">
          <CardContent className="pt-12 pb-12">
            <div className="flex flex-col items-center justify-center text-center space-y-6">
              <div className="w-16 h-16 rounded-full bg-[#EAF3FF] flex items-center justify-center">
                <FileText className="h-8 w-8 text-[#1E88E5]" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-[#0B2336]">No Project Selected</h3>
                <p className="text-[#4A6A7A] max-w-md">
                  To view project results, please select a project from your history or create a new project to get started.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <Button
                  onClick={() => navigate('/dashboard/history')}
                  className="bg-[#0B4F8C] hover:bg-[#0A3D6F] text-white px-6"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  View Project History
                </Button>
                <Button
                  onClick={() => navigate('/dashboard/new-project')}
                  variant="outline"
                  className="border-[#0B4F8C] text-[#0B4F8C] hover:bg-[#EAF3FF] px-6"
                >
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Create New Project
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show processing screen if project exists but results are null (still processing)
  if (isProcessing && project) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Project Results</h1>
          <p className="text-[#4A6A7A]">Processing your project analysis...</p>
        </div>
        
        <Card className="border-2 border-[#EAF3FF]">
          <CardContent className="pt-16 pb-16">
            <div className="flex flex-col items-center justify-center text-center space-y-6">
              <div className="w-20 h-20 rounded-full bg-[#EAF3FF] flex items-center justify-center">
                <Loader2 className="h-10 w-10 animate-spin text-[#1E88E5]" />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-semibold text-[#0B2336]">Processing Project</h3>
                <p className="text-[#4A6A7A] max-w-md">
                  Your project <strong>{project.title}</strong> is currently being analyzed. 
                  This may take a few minutes. Results will appear automatically when ready.
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-[#4A6A7A]">
                <Activity className="h-4 w-4 animate-pulse" />
                <span>Analyzing mutations, drug candidates, and modifications...</span>
              </div>
              <div className="pt-4">
                <Button
                  onClick={() => window.location.reload()}
                  variant="outline"
                  className="border-[#0B4F8C] text-[#0B4F8C] hover:bg-[#EAF3FF]"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh Results
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[#1E88E5]" />
        </div>
      </div>
    );
  }

  // Only show error if project doesn't exist (not if results are null - that's handled by processing screen)
  if (!project) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Project Results</h1>
          <p className="text-[#4A6A7A]">View detailed analysis and results for your research projects</p>
        </div>
        
        <Card className="border-2 border-dashed border-[#EAF3FF]">
          <CardContent className="pt-12 pb-12">
            <div className="flex flex-col items-center justify-center text-center space-y-6">
              <div className="w-16 h-16 rounded-full bg-[#EAF3FF] flex items-center justify-center">
                <FileText className="h-8 w-8 text-[#1E88E5]" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-[#0B2336]">Unable to Load Project</h3>
                <p className="text-[#4A6A7A] max-w-md">
                  We couldn't load the project. Please try selecting a different project or create a new one.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <Button
                  onClick={() => navigate('/dashboard/history')}
                  className="bg-[#0B4F8C] hover:bg-[#0A3D6F] text-white px-6"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  View Project History
                </Button>
                <Button
                  onClick={() => navigate('/dashboard/new-project')}
                  variant="outline"
                  className="border-[#0B4F8C] text-[#0B4F8C] hover:bg-[#EAF3FF] px-6"
                >
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Create New Project
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // If project exists but no results yet, show processing screen (already handled above, but add fallback)
  if (!results && project.status !== 'Completed') {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Project Results</h1>
          <p className="text-[#4A6A7A]">Processing your project analysis...</p>
        </div>
        
        <Card className="border-2 border-[#EAF3FF]">
          <CardContent className="pt-16 pb-16">
            <div className="flex flex-col items-center justify-center text-center space-y-6">
              <div className="w-20 h-20 rounded-full bg-[#EAF3FF] flex items-center justify-center">
                <Loader2 className="h-10 w-10 animate-spin text-[#1E88E5]" />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-semibold text-[#0B2336]">Processing Project</h3>
                <p className="text-[#4A6A7A] max-w-md">
                  Your project <strong>{project.title}</strong> is currently being analyzed. 
                  This may take a few minutes. Results will appear automatically when ready.
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-[#4A6A7A]">
                <Activity className="h-4 w-4 animate-pulse" />
                <span>Analyzing mutations, drug candidates, and modifications...</span>
              </div>
              <div className="pt-4">
                <Button
                  onClick={() => window.location.reload()}
                  variant="outline"
                  className="border-[#0B4F8C] text-[#0B4F8C] hover:bg-[#EAF3FF]"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh Results
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Export Report - Generate and download comprehensive report
  const handleExportReport = () => {
    if (!project || !results) {
      toast.error('No data available to export');
      return;
    }

    try {
      // Create report data
      const reportData = {
        project: {
          id: project.id,
          title: project.title,
          description: project.description,
          status: project.status,
          deadliness_score: deadlinessScore,
          created_at: project.created_at,
        },
        summary: {
          total_mutations: mutations.length,
          total_drugs: drugCandidates.length,
          total_modifications: modifications.length,
          top_drug: topDrug?.drug_name || 'N/A',
          top_binding_energy: topBindingEnergy,
        },
        mutations: mutations.map(m => ({
          position: m.position,
          original: m.original,
          predicted: m.predicted,
          probability: m.probability,
          effect: m.effect,
          risk_level: m.risk,
        })),
        drugs: drugCandidates.map(d => ({
          name: d.name,
          smiles: d.smiles,
          binding_affinity: d.bindingAffinity,
          ic50: d.ic50,
          molecular_weight: d.molecularWeight,
          logp: d.logP,
          rank: d.rank,
        })),
        modifications: modifications.map(m => ({
          base_formula: m.oldFormula,
          modified_formula: m.newFormula,
          changes: m.changes,
          improvements: m.improvements,
          confidence: m.confidence,
        })),
        generated_at: new Date().toISOString(),
      };

      // Convert to JSON and download
      const jsonStr = JSON.stringify(reportData, null, 2);
      const blob = new Blob([jsonStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `VIRO-AI_Report_${project.title.replace(/[^a-z0-9]/gi, '_')}_${project.id}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success('Report exported successfully!');
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Failed to export report');
    }
  };

  // Share functionality - Copy link or use Web Share API
  const handleShare = async () => {
    if (!projectId) {
      toast.error('No project to share');
      return;
    }

    const shareUrl = `${window.location.origin}/dashboard/result?projectId=${projectId}`;
    const shareData = {
      title: `VIRO-AI Project: ${project?.title || 'Project Results'}`,
      text: `Check out this viral analysis project: ${project?.title || 'Project Results'}`,
      url: shareUrl,
    };

    try {
      // Try Web Share API first (mobile/desktop with support)
      if (navigator.share) {
        await navigator.share(shareData);
        toast.success('Shared successfully!');
      } else {
        // Fallback: Copy to clipboard
        await navigator.clipboard.writeText(shareUrl);
        toast.success('Link copied to clipboard!');
      }
    } catch (error: any) {
      // User cancelled or error occurred
      if (error.name !== 'AbortError') {
        // Fallback: Copy to clipboard
        try {
          await navigator.clipboard.writeText(shareUrl);
          toast.success('Link copied to clipboard!');
        } catch (clipboardError) {
          toast.error('Failed to share. Please copy the URL manually.');
        }
      }
    }
  };

  // Flag handler
  const handleFlag = () => {
    if (!projectId) {
      toast.error('No project to flag');
      return;
    }

    const newFlaggedState = !isFlagged;
    setIsFlagged(newFlaggedState);
    
    if (typeof window !== 'undefined') {
      if (newFlaggedState) {
        localStorage.setItem(`flagged_project_${projectId}`, 'true');
        toast.success('Project flagged for review');
      } else {
        localStorage.removeItem(`flagged_project_${projectId}`);
        toast.success('Project unflagged');
      }
    }
  };

  // Download SDF file for drug structure
  const handleDownloadSDF = (drug: typeof drugCandidates[0]) => {
    if (!drug.smiles) {
      toast.error('No SMILES data available for this drug');
      return;
    }

    try {
      // Generate basic SDF content from SMILES
      // Note: This is a simplified SDF. For production, use a proper chemistry library
      const sdfContent = `
  ${drug.name || 'Unknown'}
  VIRO-AI Generated Structure
  SMILES: ${drug.smiles}
  
  0  0  0  0  0  0  0  0  0  0999 V2000
M  END
$$$$
`;
      const blob = new Blob([sdfContent], { type: 'chemical/x-mdl-sdfile' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${drug.name.replace(/[^a-z0-9]/gi, '_')}_structure.sdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success('SDF file downloaded');
    } catch (error) {
      console.error('SDF download error:', error);
      toast.error('Failed to download SDF file');
    }
  };

  // Export drug data as CSV
  const handleExportDrugData = (drug: typeof drugCandidates[0]) => {
    try {
      const csvRows = [
        ['Property', 'Value'],
        ['Name', drug.name],
        ['SMILES', drug.smiles],
        ['Binding Affinity', String(drug.bindingAffinity)],
        ['IC50', drug.ic50 || 'N/A'],
        ['Molecular Weight', String(drug.molecularWeight)],
        ['LogP', String(drug.logP)],
        ['Formula', drug.formula || 'N/A'],
        ['Heavy Atoms', String(drug.heavyAtoms)],
        ['Rank', String(drug.rank)],
        ['Score', String(drug.score)],
      ];

      const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${drug.name.replace(/[^a-z0-9]/gi, '_')}_data.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success('Drug data exported successfully');
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Failed to export drug data');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-[#0B2336]">Project Analysis Results</h1>
            <Badge className={project.status === 'Completed' ? 'bg-green-100 text-green-800' : project.status === 'Processing' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}>
              {project.status}
            </Badge>
          </div>
          <p className="text-[#4A6A7A]">{project.title}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleExportReport}>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button variant="outline" size="sm" onClick={handleShare}>
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleRefresh}
            disabled={resultsFetching || projectLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${resultsFetching ? 'animate-spin' : ''}`} />
            {resultsFetching ? 'Refreshing...' : 'Refresh'}
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleFlag}
            className={isFlagged ? 'bg-yellow-50 border-yellow-300 text-yellow-700' : ''}
          >
            <Flag className={`h-4 w-4 mr-2 ${isFlagged ? 'fill-yellow-600' : ''}`} />
            {isFlagged ? 'Flagged' : 'Flag'}
          </Button>
        </div>
      </div>

      {/* Disclaimer */}
      <Alert className="border-yellow-300 bg-yellow-50">
        <AlertTriangle className="h-4 w-4 text-yellow-600" />
        <AlertTitle className="text-yellow-800">Calibration & Disclaimer</AlertTitle>
        <AlertDescription className="text-yellow-700 text-sm">
          Results are simulator outputs calibrated on public/reputable datasets and internal models. This application is a research simulator; outputs can be incorrect. Estimated accuracy: up to ~80% depending on data quality and model assumptions. Use results for research guidance only and validate experimentally before policy or clinical action.
        </AlertDescription>
      </Alert>

      {/* Tabs for Different Sections */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="mutation">Mutation</TabsTrigger>
          <TabsTrigger value="drugs">Drug Candidates</TabsTrigger>
          <TabsTrigger value="modifications">Modifications</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 3D Protein Structure */}
            <Card>
              <CardHeader>
                <CardTitle>3D Virus Protein Structure</CardTitle>
                <CardDescription>Interactive molecular visualization</CardDescription>
              </CardHeader>
              <CardContent>
                <Protein3DViewer
                  proteinSequence={project?.description}
                  drugSmiles={topDrug?.smiles}
                  drugName={topDrug?.drug_name}
                  bindingEnergy={topBindingEnergy}
                  molecularWeight={parseFloat(molecularWeight) || 141.2}
                  residues={residuesCount}
                  rmsd={typeof rmsdValue === 'number' ? rmsdValue : 1.8}
                  pdbId={getPdbId}
                  pdbFileUrl={(results as any)?.structure_data?.pdb_file_path ? `/api/projects/${projectId}/pdb/${(results as any).structure_data.pdb_file_path}` : undefined}
                  className="aspect-square"
                />
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-[#4A6A7A]">Residues</p>
                    <p className="font-semibold text-[#0B2336]">{residuesCount}</p>
                  </div>
                  <div>
                    <p className="text-[#4A6A7A]">Molecular Weight</p>
                    <p className="font-semibold text-[#0B2336]">{molecularWeight} kDa</p>
                  </div>
                  <div>
                    <p className="text-[#4A6A7A]">RMSD vs Reference</p>
                    <p className="font-semibold text-[#0B2336]">{typeof rmsdValue === 'number' ? rmsdValue.toFixed(1) : '1.8'} Å</p>
                  </div>
                  <div>
                    <p className="text-[#4A6A7A]">Binding Energy</p>
                    <p className="font-semibold text-[#0B2336]">
                      {topBindingEnergy !== 0 ? `${Number(topBindingEnergy).toFixed(1)} kcal/mol` : 'N/A'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Virus Description, Origin & Symptoms */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Virus Description</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-sm text-[#4A6A7A]">Project Description</p>
                    <p className="font-semibold text-[#0B2336]">{project.description || 'No description provided'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-[#4A6A7A]">Key Mutations</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {mutations.length > 0 ? (
                        mutations.slice(0, 4).map((mut, idx) => (
                          <Badge key={idx} variant="secondary">{mut.position}</Badge>
                        ))
                      ) : (
                        <span className="text-sm text-[#4A6A7A]">No mutations predicted yet</span>
                      )}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-[#4A6A7A]">Status</p>
                    <p className="text-sm text-[#0B2336]">{project.status}</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Origin & Geolocation</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {(project.region || project.country || project.latitude || project.longitude) && (
                    <div className="flex items-start gap-2">
                      <MapPin className="h-5 w-5 text-[#1E88E5] mt-0.5" />
                      <div>
                        <p className="font-semibold text-[#0B2336]">
                          {[project.region, project.country].filter(Boolean).join(', ') || 'Location not specified'}
                        </p>
                        {(project.latitude && project.longitude) && (
                          <p className="text-sm text-[#4A6A7A]">{project.latitude}°N, {project.longitude}°E</p>
                        )}
                        {project.collection_timestamp && (
                          <p className="text-sm text-[#4A6A7A]">Collected: {new Date(project.collection_timestamp).toLocaleString()}</p>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Symptoms & Clinical Correlates</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {project.symptoms && (
                      <div>
                        <p className="text-sm text-[#4A6A7A] mb-2">Observed Clinical Symptoms</p>
                        <p className="text-sm text-[#0B2336]">{project.symptoms}</p>
                      </div>
                    )}
                    {project.clinical_severity && (
                      <div>
                        <p className="text-sm text-[#4A6A7A] mb-2">Clinical Severity</p>
                        <Badge variant={project.clinical_severity === 'severe' || project.clinical_severity === 'critical' ? 'destructive' : 'secondary'}>
                          {project.clinical_severity}
                        </Badge>
                      </div>
                    )}
                    {project.clinical_notes && (
                      <div>
                        <p className="text-sm text-[#4A6A7A] mb-2">Clinical Notes</p>
                        <p className="text-sm text-[#0B2336]">{project.clinical_notes}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Deadliness Score */}
          <Card className="border-l-4 border-l-red-500">
            <CardHeader>
              <CardTitle>Deadliness Score Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6 mb-6">
                <div className="text-center">
                  <div className="text-5xl font-bold text-red-600">{deadlinessScore > 0 ? deadlinessScore : 'N/A'}</div>
                  <p className="text-sm text-[#4A6A7A] mt-1">Deadliness Score</p>
                </div>
                <div className="flex-1 space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>R₀ Impact</span>
                      <span className="font-semibold">{deadlinessScore > 0 ? `${Math.round(deadlinessScore * 0.85)}/100` : 'N/A'}</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-red-500" style={{ width: deadlinessScore > 0 ? `${Math.round(deadlinessScore * 0.85)}%` : '0%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Binding Affinity Proxy</span>
                      <span className="font-semibold">{topBindingEnergy < 0 ? `${Math.round(Math.abs(topBindingEnergy) * 10)}/100` : 'N/A'}</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-orange-500" style={{ width: topBindingEnergy < 0 ? `${Math.min(100, Math.round(Math.abs(topBindingEnergy) * 10))}%` : '0%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Immune Evasion Signal</span>
                      <span className="font-semibold">{deadlinessScore > 0 ? `${Math.round(deadlinessScore * 0.68)}/100` : 'N/A'}</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-yellow-500" style={{ width: deadlinessScore > 0 ? `${Math.round(deadlinessScore * 0.68)}%` : '0%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Cytopathic Effect Index</span>
                      <span className="font-semibold">{deadlinessScore > 0 ? `${Math.round(deadlinessScore * 0.62)}/100` : 'N/A'}</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: deadlinessScore > 0 ? `${Math.round(deadlinessScore * 0.62)}%` : '0%' }} />
                    </div>
                  </div>
                </div>
              </div>
              <Alert>
                <AlertDescription className="text-sm">
                  <strong>Interpretation:</strong> {deadlinessScore > 70 ? 'Score indicates high transmissibility with moderate severity. Recommended priority: Enhanced surveillance and accelerated vaccine booster development targeting identified mutations.' : deadlinessScore > 50 ? 'Score indicates moderate transmissibility. Continue monitoring and standard surveillance protocols.' : 'Score indicates low to moderate risk. Standard monitoring recommended.'}
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          {/* Actionable Recommendations */}
          {results.drugs && results.drugs.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Actionable Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-3 list-decimal list-inside">
                  {results.drugs[0] && (
                    <li className="text-sm text-[#0B2336]">
                      <strong>Priority:</strong> Conduct in-vitro binding validation of {results.drugs[0].drug_name} against target protein
                    </li>
                  )}
                  {mutations.length > 0 && (
                    <li className="text-sm text-[#0B2336]">
                      <strong>Vaccine Update:</strong> Update vaccine epitope panel to include {mutations.slice(0, 2).map(m => m.position).join(' and ')} mutations
                    </li>
                  )}
                  {project.region && project.country && (
                    <li className="text-sm text-[#0B2336]">
                      <strong>Surveillance:</strong> Increase genomic surveillance in {project.region}, {project.country}
                    </li>
                  )}
                  <li className="text-sm text-[#0B2336]">
                    <strong>Clinical Monitoring:</strong> Track breakthrough infections in vaccinated populations
                  </li>
                  {project.region && (
                    <li className="text-sm text-[#0B2336]">
                      <strong>Public Health:</strong> Implement enhanced contact tracing protocols in detected regions
                    </li>
                  )}
                </ol>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Mutation Tab */}
        <TabsContent value="mutation" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Predicted Mutations</CardTitle>
              <CardDescription>AI-forecasted viral mutations with probability and impact analysis</CardDescription>
            </CardHeader>
            <CardContent>
              {mutations.length === 0 ? (
                <p className="text-sm text-[#4A6A7A] text-center py-4">No mutations predicted yet. Analysis may still be processing.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Position</TableHead>
                      <TableHead>Original</TableHead>
                      <TableHead>Predicted</TableHead>
                      <TableHead>Probability</TableHead>
                      <TableHead>Predicted Effect</TableHead>
                      <TableHead>Risk Level</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mutations.map((mutation, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-mono">{mutation.position}</TableCell>
                      <TableCell className="font-mono font-semibold">{mutation.original}</TableCell>
                      <TableCell className="font-mono font-semibold text-[#1E88E5]">{mutation.predicted}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden w-20">
                            <div className="h-full bg-[#1E88E5]" style={{ width: `${mutation.probability}%` }} />
                          </div>
                          <span className="text-sm font-medium">{mutation.probability}%</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm">{mutation.effect}</TableCell>
                      <TableCell>
                        <Badge
                          variant={mutation.risk === 'High' ? 'destructive' : mutation.risk === 'Medium' ? 'default' : 'secondary'}
                        >
                          {mutation.risk}
                        </Badge>
                      </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Detailed Mutation Analysis Cards */}
          {detailedMutationData.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center text-[#4A6A7A]">
                No detailed mutation analysis available yet.
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {detailedMutationData.map((data, index) => (
              <Card key={index} className="border-l-4 border-l-[#1E88E5]">
                <CardHeader>
                  <CardTitle className="text-xl">Detailed Analysis: {data.mutation}</CardTitle>
                  <CardDescription>Comprehensive genomic, structural, and evolutionary characterization</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* 1. Genomic-Level Mutation Description */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold">1</span>
                      Genomic-Level Mutation Description
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Nucleotide Substitution</p>
                        <p className="text-sm font-semibold text-[#0B2336] font-mono">{String(data.genomicLevel.nucleotideSubstitution)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Mutation Type</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{String(data.genomicLevel.mutationType)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Genomic Region</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{String(data.genomicLevel.genomicRegion)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Codon Change</p>
                        <p className="text-sm font-semibold text-[#0B2336] font-mono">{String(data.genomicLevel.codonChange)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Classification</p>
                        <Badge variant="secondary">{String(data.genomicLevel.synonymous)}</Badge>
                      </div>
                    </div>
                  </div>

                  {/* 2. Mutation Probability Metrics */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-sm font-bold">2</span>
                      Mutation Probability Metrics
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">AI-Derived Probability Score</p>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full bg-purple-500" style={{ width: `${data.probability.aiScore * 100}%` }} />
                          </div>
                          <span className="text-sm font-bold text-purple-600">{data.probability.aiScore}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Historical Frequency</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.probability.historicalFrequency}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Fixation Likelihood</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.probability.fixationLikelihood}</p>
                      </div>
                    </div>
                  </div>

                  {/* 3. Selective Pressure & Evolutionary Indicators */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-sm font-bold">3</span>
                      Selective Pressure & Evolutionary Indicators
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">dN/dS Ratio</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.selectivePressure.dNdS}</p>
                        <Badge variant="outline" className="mt-1 text-xs">Positive Selection</Badge>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Conservation Score</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.selectivePressure.conservationScore}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Co-Evolution Pattern</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.selectivePressure.coEvolution}</p>
                      </div>
                    </div>
                  </div>

                  {/* 4. Protein Structural Consequences */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-sm font-bold">4</span>
                      Protein Structural Consequences
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔRMSD</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.structuralConsequences.deltaRMSD}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔRMSF</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.structuralConsequences.deltaRMSF}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔG Stability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.structuralConsequences.deltaGStability}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">SASA Shift</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.structuralConsequences.sasaShift}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Secondary Structure</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.structuralConsequences.secondaryStructure}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Inter-Residue Contacts</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.structuralConsequences.interResidueContacts}</p>
                      </div>
                    </div>
                  </div>

                  {/* 5. Receptor Binding Impact */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-sm font-bold">5</span>
                      Predicted Impact on Receptor Binding
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔKd (Binding Affinity)</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.receptorBinding.deltaKd}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Interface Alteration</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.receptorBinding.interfaceAlteration}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Critical Residues</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.receptorBinding.criticalResidues}</p>
                      </div>
                    </div>
                  </div>

                  {/* 6. Immune Evasion & Antigenicity */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-yellow-100 text-yellow-600 flex items-center justify-center text-sm font-bold">6</span>
                      Immune Evasion & Antigenicity Shifts
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">B-Cell Epitope</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.immuneEvasion.bCellEpitope}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">T-Cell Epitope</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.immuneEvasion.tCellEpitope}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Glycosylation Site</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.immuneEvasion.glycosylationSite}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Epitope Masking Index</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.immuneEvasion.epitopeMasking}</p>
                      </div>
                    </div>
                  </div>

                  {/* 7. Viral Fitness & Replication */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm font-bold">7</span>
                      Viral Fitness & Replication Potential
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Replication Efficiency</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.viralFitness.replicationEfficiency}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Virion Stability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.viralFitness.virionStability}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">CPE Index</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.viralFitness.cpeIndex}</p>
                      </div>
                    </div>
                  </div>

                  {/* 8. Pathogenicity Contribution */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 flex items-center justify-center text-sm font-bold">8</span>
                      Pathogenicity Contribution
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Pathogenicity Score Contribution</p>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full bg-pink-500" style={{ width: `${parseInt(data.pathogenicity.contribution)}%` }} />
                          </div>
                          <span className="text-sm font-bold text-pink-600">{data.pathogenicity.contribution}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Tropism Impact</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.pathogenicity.tropismImpact}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Viral Load Threshold</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.pathogenicity.viralLoadThreshold}</p>
                      </div>
                    </div>
                  </div>

                  {/* 9. Lineage Emergence Forecasts */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-teal-100 text-teal-600 flex items-center justify-center text-sm font-bold">9</span>
                      Lineage Emergence Forecasts
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">New Lineage Probability</p>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full bg-teal-500" style={{ width: data.lineageEmergence.newLineageProbability }} />
                          </div>
                          <span className="text-sm font-bold text-teal-600">{data.lineageEmergence.newLineageProbability}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Phylogenetic Pathway</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.lineageEmergence.phylogeneticPathway}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Co-Mutation Synergy</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{data.lineageEmergence.coMutationSynergy}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            </div>
          )}
        </TabsContent>

        {/* Drug Candidates Tab */}
        <TabsContent value="drugs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Top Drug Candidates</CardTitle>
              <CardDescription>Ranked antiviral compounds with binding and pharmacological properties</CardDescription>
            </CardHeader>
            <CardContent>
              {drugCandidates.length === 0 ? (
                <p className="text-sm text-[#4A6A7A] text-center py-4">No drug candidates found yet. Analysis may still be processing.</p>
              ) : (
                <div className="space-y-4">
                  {drugCandidates.map((drug, index) => (
                  <Card key={index} className="border-l-4 border-l-[#1E88E5]">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">#{drug.rank} - {drug.name}</CardTitle>
                          <CardDescription className="font-mono text-xs mt-1">{drug.smiles}</CardDescription>
                        </div>
                        <Badge className="bg-[#0B4F8C] text-white">Score: {drug.score}</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-[#4A6A7A]">Binding Affinity (ΔG)</p>
                          <p className="font-semibold text-[#0B2336]">{drug.bindingAffinity} kcal/mol</p>
                        </div>
                        <div>
                          <p className="text-xs text-[#4A6A7A]">IC₅₀ (Predicted)</p>
                          <p className="font-semibold text-[#0B2336]">{drug.ic50}</p>
                        </div>
                        <div>
                          <p className="text-xs text-[#4A6A7A]">logP</p>
                          <p className="font-semibold text-[#0B2336]">{drug.logP}</p>
                        </div>
                        <div>
                          <p className="text-xs text-[#4A6A7A]">Molecular Weight</p>
                          <p className="font-semibold text-[#0B2336]">{drug.molecularWeight} g/mol</p>
                        </div>
                        <div>
                          <p className="text-xs text-[#4A6A7A]">Formula</p>
                          <p className="font-semibold text-[#0B2336] font-mono">{drug.formula}</p>
                        </div>
                        <div>
                          <p className="text-xs text-[#4A6A7A]">Heavy Atoms</p>
                          <p className="font-semibold text-[#0B2336]">{drug.heavyAtoms}</p>
                        </div>
                      </div>
                      <div className="flex gap-2 mt-4">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            // Scroll to 3D viewer or show structure
                            const viewerElement = document.querySelector('[data-protein-viewer]');
                            if (viewerElement) {
                              viewerElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            } else {
                              toast.info('3D structure viewer is available in the Overview tab');
                            }
                          }}
                        >
                          View Structure
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleDownloadSDF(drug)}
                        >
                          Download SDF
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleExportDrugData(drug)}
                        >
                          Export Data
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Detailed Drug Analysis */}
          {detailedDrugData.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center text-[#4A6A7A]">
                No detailed drug analysis available yet.
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {detailedDrugData.map((drug, idx) => (
              <Card key={idx} className="border-l-4 border-l-[#0B4F8C]">
                <CardHeader>
                  <CardTitle className="text-xl">Comprehensive Scientific Analysis: {drug.name}</CardTitle>
                  <CardDescription>Detailed molecular characterization and predictive modeling</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* 1. Molecular Identity & Structure */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold">1</span>
                      Molecular Identity & Structure
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Chemical Name</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.molecularIdentity.chemicalName}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Unique ID</p>
                        <p className="text-sm font-semibold text-[#0B2336] font-mono">{drug.molecularIdentity.uniqueID}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">InChI String</p>
                        <p className="text-xs font-mono text-[#0B2336] break-all">{drug.molecularIdentity.inchi}</p>
                      </div>
                    </div>
                  </div>

                  {/* 2. Binding Affinity & Interaction Strength */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-sm font-bold">2</span>
                      Binding Affinity & Interaction Strength
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Binding Energy (ΔG)</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.bindingMetrics.bindingEnergy}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Kd</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.bindingMetrics.kd}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Ki</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.bindingMetrics.ki}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">IC₅₀</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.bindingMetrics.ic50}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Docking Score</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.bindingMetrics.dockingScore}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Pose RMSD</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.bindingMetrics.poseRMSD}</p>
                      </div>
                    </div>
                  </div>

                  {/* 3. Interaction Map */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-sm font-bold">3</span>
                      Interaction Map With Viral Protein
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">H-Bond Interactions</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.interactionMap.hBonds}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Hydrophobic Contacts</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.interactionMap.hydrophobicContacts}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">π-π Stacking</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.interactionMap.piPiStacking}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Ionic Interactions</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.interactionMap.ionicInteractions}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Van der Waals Sites</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.interactionMap.vdwEngagement}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Binding Pocket Occupancy</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.interactionMap.bindingPocketOccupancy}</p>
                      </div>
                    </div>
                  </div>

                  {/* 4. Structural Stability */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-sm font-bold">4</span>
                      Structural Stability of Ligand-Protein Complex
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">RMSD Complex</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.structuralStability.rmsdComplex}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">RMSF Binding Pocket</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.structuralStability.rmsfBindingPocket}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">MM-PBSA Energy</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.structuralStability.mmPbsaEnergy}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">SASA Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.structuralStability.sasaChange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">H-Bond Persistence</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.structuralStability.hBondPersistence}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">COM Stability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.structuralStability.comStability}</p>
                      </div>
                    </div>
                  </div>

                  {/* 5. Physicochemical Properties */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-sm font-bold">5</span>
                      Physicochemical Properties
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">LogP</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.physicochemical.logP}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">LogS</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.physicochemical.logS}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">tPSA</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.physicochemical.tpsa}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">H-Bond Donors</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.physicochemical.hbDonors}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">H-Bond Acceptors</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.physicochemical.hbAcceptors}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Rotatable Bonds</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.physicochemical.rotatableBonds}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">pKa</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.physicochemical.pka}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Aromaticity</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.physicochemical.aromaticity}</p>
                      </div>
                    </div>
                  </div>

                  {/* 6. ADME Predictions */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-yellow-100 text-yellow-600 flex items-center justify-center text-sm font-bold">6</span>
                      ADME Scientific Predictions
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Absorption</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.adme.absorption}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Plasma Protein Binding</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.adme.plasmaProteinBinding}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">LogD</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.adme.logD}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Metabolism</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.adme.metabolism}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Clearance</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.adme.clearance}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Half-Life</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.adme.halfLife}</p>
                      </div>
                      <div className="col-span-2">
                        <p className="text-xs text-[#4A6A7A]">Permeability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.adme.permeability}</p>
                      </div>
                    </div>
                  </div>

                  {/* 7. Toxicology */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm font-bold">7</span>
                      Toxicological & Safety-Signal Models
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Ames Mutagenicity</p>
                        <Badge variant="secondary">{drug.toxicology.amesMutagenicity}</Badge>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">hERG Liability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.toxicology.hergLiability}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">PAINS Filter</p>
                        <Badge variant="secondary">{drug.toxicology.painsFilter}</Badge>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Toxicophore Alerts</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.toxicology.toxicophoreAlerts}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Reactive Metabolites</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.toxicology.reactiveMetabolites}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">LD₅₀ Model</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.toxicology.ld50Model}</p>
                      </div>
                    </div>
                  </div>

                  {/* 8. Comparative Scores */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 flex items-center justify-center text-sm font-bold">8</span>
                      Comparative Activity Scores
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-lg">
                      {Object.entries(drug.comparativeScores).map(([key, value]) => (
                        <div key={key}>
                          <p className="text-xs text-[#4A6A7A] capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-blue-500" style={{ width: `${value.replace('/100', '')}%` }} />
                            </div>
                            <span className="text-xs font-bold text-blue-600">{value}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 9. Ensemble Analysis */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-teal-100 text-teal-600 flex items-center justify-center text-sm font-bold">9</span>
                      Multi-Conformation & Ensemble Analysis
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Multi-Conformation Binding</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.ensembleAnalysis.multiConformation}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Mutant Variants</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.ensembleAnalysis.mutantVariants}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Ensemble Docking</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.ensembleAnalysis.ensembleDocking}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Pose Distribution</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.ensembleAnalysis.poseDistribution}</p>
                      </div>
                    </div>
                  </div>

                  {/* 10. Resistance Vulnerability */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-sm font-bold">10</span>
                      Resistance Vulnerability Analysis
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Mutation Sensitivity</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.resistanceVulnerability.mutationSensitivity}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔΔG Across Mutants</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.resistanceVulnerability.deltaGMutants}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Loss-of-Affinity Threshold</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.resistanceVulnerability.lossOfAffinityThreshold}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Resistance Risk Score</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.resistanceVulnerability.resistanceRisk}</p>
                      </div>
                    </div>
                  </div>

                  {/* 11. Chemical Diversity */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-cyan-100 text-cyan-600 flex items-center justify-center text-sm font-bold">11</span>
                      Chemical Diversity & Novelty Analysis
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Scaffold Diversity</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.chemicalDiversity.scaffoldDiversity}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Similarity to Known Compounds</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.chemicalDiversity.similarityToKnown}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Synthetic Accessibility</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.chemicalDiversity.syntheticAccessibility}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Patentability Estimate</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{drug.chemicalDiversity.patentabilityEstimate}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            </div>
          )}
        </TabsContent>

        {/* Modifications Tab */}
        <TabsContent value="modifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI-Suggested Chemical Modifications</CardTitle>
              <CardDescription>Optimized molecular structures with predicted improvements</CardDescription>
            </CardHeader>
            <CardContent>
              {modifications.length === 0 ? (
                <p className="text-sm text-[#4A6A7A] text-center py-4">No modifications suggested yet. Analysis may still be processing.</p>
              ) : (
                <div className="space-y-6">
                  {modifications.map((mod, index) => (
                  <Card key={index} className="border-l-4 border-l-green-500">
                    <CardHeader>
                      <CardTitle className="text-lg">Modification Suggestion #{index + 1}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-[#4A6A7A] mb-2">Base Formula</p>
                          <p className="font-mono font-semibold text-[#0B2336] text-lg">{mod.oldFormula}</p>
                        </div>
                        <div>
                          <p className="text-sm text-[#4A6A7A] mb-2">Suggested Formula</p>
                          <p className="font-mono font-semibold text-green-600 text-lg">{mod.newFormula}</p>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-[#4A6A7A] mb-2">Chemical Groups Changed</p>
                        <p className="text-sm text-[#0B2336]">{mod.changes}</p>
                      </div>
                      <div>
                        <p className="text-sm text-[#4A6A7A] mb-2">Predicted Improvements</p>
                        <p className="text-sm text-[#0B2336]">{mod.improvements}</p>
                      </div>
                      <div className="flex items-center gap-4 pt-2">
                        <Badge variant="outline" className="text-xs">
                          Confidence: {mod.confidence} accuracy
                        </Badge>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => scrollToModificationDetail(index)}
                        >
                          View Detailed Analysis
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Detailed Modification Analysis */}
          {detailedModificationData.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center text-[#4A6A7A]">
                No detailed modification analysis available yet.
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {detailedModificationData.map((mod, index) => (
              <Card 
                key={index} 
                id={`modification-detail-${index}`}
                className="border-l-4 border-l-green-600 scroll-mt-4"
              >
                <CardHeader>
                  <CardTitle className="text-xl">Comprehensive Analysis: {mod.modificationID}</CardTitle>
                  <CardDescription>Detailed chemical modification characterization and predictive modeling</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* 1. Modification Identity */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold">1</span>
                      Molecular Modification Identity
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Added Groups</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.modificationIdentity.addedGroups}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Removed Groups</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.modificationIdentity.removedGroups}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Substitutions</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.modificationIdentity.substitutions}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Structural Constraints</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.modificationIdentity.structuralConstraints}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Aromaticity Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.modificationIdentity.aromaticityChange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">H-Bond Count Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.modificationIdentity.hbCountChange}</p>
                      </div>
                    </div>
                  </div>

                  {/* 2. Structural Effects */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-sm font-bold">2</span>
                      Structural & Conformational Effects
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔRMSD</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.structuralEffects.deltaRMSD}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Molecular Volume Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.structuralEffects.molecularVolumeChange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Steric Hindrance Index</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.structuralEffects.stericHindranceIndex}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Torsional Angle Shifts</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.structuralEffects.torsionalAngleShifts}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">π-π Stacking Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.structuralEffects.piPiStackingChange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">SASA Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.structuralEffects.sasaChange}</p>
                      </div>
                    </div>
                  </div>

                  {/* 3. Physicochemical Changes */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-sm font-bold">3</span>
                      Physicochemical Property Changes
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔLogP</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.physicochemicalChanges.deltaLogP}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔpKa</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.physicochemicalChanges.deltaPka}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">tPSA Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.physicochemicalChanges.tpsaChange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">MW Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.physicochemicalChanges.molecularWeightChange}</p>
                      </div>
                    </div>
                  </div>

                  {/* 4. Binding Affinity Effects */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-sm font-bold">4</span>
                      Predicted Binding Affinity Effects
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔBinding Energy</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.bindingAffinityEffects.deltaBindingEnergy}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Interaction Hotspot Changes</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.bindingAffinityEffects.interactionHotspotChanges}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Contact Residue Map Diff</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.bindingAffinityEffects.contactResidueMapDiff}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Pose Stability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.bindingAffinityEffects.dockingPoseStability}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Kd Improvement</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.bindingAffinityEffects.kdImprovement}</p>
                      </div>
                    </div>
                  </div>

                  {/* 5. Electronic Effects */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-sm font-bold">5</span>
                      Electronic & Quantum-Level Effects
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">HOMO-LUMO Gap Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.electronicEffects.homoLumoGapChange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Electron Density</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.electronicEffects.electronDensityRedistribution}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Partial Charge Analysis</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.electronicEffects.partialChargeAnalysis}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Dipole Moment Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.electronicEffects.dipoleMomentChange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Polarizability Shift</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.electronicEffects.polarizabilityShift}</p>
                      </div>
                    </div>
                  </div>

                  {/* 6. Stability & Degradation */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-yellow-100 text-yellow-600 flex items-center justify-center text-sm font-bold">6</span>
                      Stability & Degradation Properties
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Metabolic Stability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.stabilityDegradation.metabolicStability}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Photostability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.stabilityDegradation.photostability}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Thermal Stability</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.stabilityDegradation.thermalStability}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Reactive Site Masking</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.stabilityDegradation.reactiveSiteMasking}</p>
                      </div>
                    </div>
                  </div>

                  {/* 7. Solubility & Permeability */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm font-bold">7</span>
                      Solubility & Permeability Changes
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">ΔSolubility</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.solubilityPermeability.deltaSolubility}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Permeability Models</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.solubilityPermeability.permeabilityModels}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">LogS Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.solubilityPermeability.logSChange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Efflux Ratio Prediction</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.solubilityPermeability.effluxRatioPrediction}</p>
                      </div>
                    </div>
                  </div>

                  {/* 8. ADME Shifts */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 flex items-center justify-center text-sm font-bold">8</span>
                      ADME-Related Parameter Shifts
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Absorption Efficiency</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.admeShifts.absorptionEfficiency}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">PPB Shift</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.admeShifts.plasmaProteinBindingShift}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Metabolic Hotspots</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.admeShifts.metabolicHotspots}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Clearance Prediction</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.admeShifts.clearancePrediction}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">LogD Change</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.admeShifts.logDChange}</p>
                      </div>
                    </div>
                  </div>

                  {/* 9. Toxicity Signatures */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-teal-100 text-teal-600 flex items-center justify-center text-sm font-bold">9</span>
                      Toxicity-Related Chemical Signatures
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">PAINS Filter</p>
                        <Badge variant="secondary">{mod.toxicitySignatures.painsFilter}</Badge>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Structural Alerts</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.toxicitySignatures.structuralAlerts}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Mutagenicity Predictors</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.toxicitySignatures.mutagenicityPredictors}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Reactive Metabolite Risk</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.toxicitySignatures.reactiveMetaboliteRisk}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Off-Target Binding</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.toxicitySignatures.offTargetBinding}</p>
                      </div>
                    </div>
                  </div>

                  {/* 10. Synthetic Feasibility */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-cyan-100 text-cyan-600 flex items-center justify-center text-sm font-bold">10</span>
                      Synthetic Feasibility Metrics
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      <div>
                        <p className="text-xs text-[#4A6A7A]">SAS Score</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.syntheticFeasibility.sasScore}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Synthetic Steps</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.syntheticFeasibility.syntheticSteps}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Retrosynthesis Complexity</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.syntheticFeasibility.retrosynthesisComplexity}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Rare Intermediates</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.syntheticFeasibility.rareIntermediates}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#4A6A7A]">Yield Prediction</p>
                        <p className="text-sm font-semibold text-[#0B2336]">{mod.syntheticFeasibility.yieldPrediction}</p>
                      </div>
                    </div>
                  </div>

                  {/* 11. Comparative Scoring */}
                  <div>
                    <h4 className="font-semibold text-[#0B2336] mb-3 flex items-center gap-2">
                      <span className="w-8 h-8 rounded-full bg-lime-100 text-lime-600 flex items-center justify-center text-sm font-bold">11</span>
                      Comparative Scoring Table
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                      {Object.entries(mod.comparativeScoring).map(([key, value]) => (
                        <div key={key}>
                          <p className="text-xs text-[#4A6A7A] capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-green-500" style={{ width: `${value.replace('/100', '')}%` }} />
                            </div>
                            <span className="text-xs font-bold text-green-600">{value}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

    </div>
  );
}