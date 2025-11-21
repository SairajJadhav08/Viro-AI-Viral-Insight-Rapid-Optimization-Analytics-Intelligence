import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Upload, FileText, AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useNavigate } from 'react-router-dom';
import { useCreateProject } from '@/hooks/use-projects';
import { toast } from 'sonner';

export default function NewProject() {
  const navigate = useNavigate();
  const createProject = useCreateProject();
  const [projectData, setProjectData] = useState({
    title: '',
    description: '',
    proteinFiles: [] as File[],
    clinicalFiles: [] as File[],
    assayFiles: [] as File[],
    latitude: '',
    longitude: '',
    country: '',
    region: '',
    timestamp: '',
    symptoms: '',
    severity: '',
    notes: ''
  });

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: 'protein' | 'clinical' | 'assay') => {
    const files = Array.from(e.target.files || []);
    if (type === 'protein') {
      setProjectData({ ...projectData, proteinFiles: files });
    } else if (type === 'clinical') {
      setProjectData({ ...projectData, clinicalFiles: files });
    } else {
      setProjectData({ ...projectData, assayFiles: files });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (projectData.proteinFiles.length === 0) {
      return;
    }

    // Check if user is authenticated before submitting
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (!token) {
      toast.error('Please sign in to create a project');
      navigate('/login');
      return;
    }

    createProject.mutate({
      title: projectData.title,
      description: projectData.description || undefined,
      proteinFiles: projectData.proteinFiles,
      clinicalFiles: projectData.clinicalFiles,
      assayFiles: projectData.assayFiles,
      latitude: projectData.latitude ? parseFloat(projectData.latitude) : undefined,
      longitude: projectData.longitude ? parseFloat(projectData.longitude) : undefined,
      country: projectData.country || undefined,
      region: projectData.region || undefined,
      collection_timestamp: projectData.timestamp || undefined,
      symptoms: projectData.symptoms || undefined,
      clinical_severity: projectData.severity || undefined,
      clinical_notes: projectData.notes || undefined,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#0B2336] mb-2">New Project</h1>
        <p className="text-[#4A6A7A]">Create a new viral analysis project</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Project Basics */}
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
            <CardDescription>Basic details about your research project</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="title">Project Title *</Label>
              <Input
                id="title"
                required
                value={projectData.title}
                onChange={(e) => setProjectData({ ...projectData, title: e.target.value })}
                placeholder="e.g., SARS-CoV-2 Variant Analysis - Delta Sublineage"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={projectData.description}
                onChange={(e) => setProjectData({ ...projectData, description: e.target.value })}
                placeholder="Brief overview of research aims and objectives"
                className="mt-1"
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* File Uploads */}
        <Card>
          <CardHeader>
            <CardTitle>Data Upload</CardTitle>
            <CardDescription>Upload viral sequences, protein structures, and clinical data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Protein Structure Upload */}
            <div>
              <Label htmlFor="protein-upload">Virus Protein Structure(s) *</Label>
              <Alert className="mt-2 mb-3">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-xs">
                  Accepted formats: .fasta, .fa, .pdb, .cif, .mmcif | Max file size: 250 MB
                </AlertDescription>
              </Alert>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-[#1E88E5] transition-colors">
                <Upload className="h-12 w-12 text-[#4A6A7A] mx-auto mb-3" />
                <Input
                  id="protein-upload"
                  type="file"
                  multiple
                  accept=".fasta,.fa,.pdb,.cif,.mmcif"
                  onChange={(e) => handleFileUpload(e, 'protein')}
                  className="hidden"
                />
                <Label htmlFor="protein-upload" className="cursor-pointer">
                  <Button type="button" variant="outline" onClick={() => document.getElementById('protein-upload')?.click()}>
                    Choose Files
                  </Button>
                </Label>
                {projectData.proteinFiles.length > 0 && (
                  <div className="mt-3 space-y-1">
                    {projectData.proteinFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-center gap-2 text-sm text-[#0B4F8C]">
                        <FileText className="h-4 w-4" />
                        <span>{file.name} ({(file.size / 1024).toFixed(2)} KB)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Clinical Data Upload */}
            <div>
              <Label htmlFor="clinical-upload">Clinical Data (CSV)</Label>
              <Alert className="mt-2 mb-3">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-xs">
                  Required columns: patient_id, age, onset_date, symptom_codes, lab_results
                </AlertDescription>
              </Alert>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-[#1E88E5] transition-colors">
                <Upload className="h-12 w-12 text-[#4A6A7A] mx-auto mb-3" />
                <Input
                  id="clinical-upload"
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileUpload(e, 'clinical')}
                  className="hidden"
                />
                <Label htmlFor="clinical-upload" className="cursor-pointer">
                  <Button type="button" variant="outline" onClick={() => document.getElementById('clinical-upload')?.click()}>
                    Choose File
                  </Button>
                </Label>
                {projectData.clinicalFiles.length > 0 && (
                  <div className="mt-3 text-sm text-[#0B4F8C] flex items-center justify-center gap-2">
                    <FileText className="h-4 w-4" />
                    <span>{projectData.clinicalFiles[0].name}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Assay Upload (Optional) */}
            <div>
              <Label htmlFor="assay-upload">Experimental Assays (CSV) - Optional</Label>
              <Alert className="mt-2 mb-3">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-xs">
                  Accepted formats: .csv, .tsv, .xlsx | CSV must contain columns: <strong>name</strong> (compound name) and <strong>smiles</strong> (SMILES notation). Optional columns: ic50, binding_energy, docking_score, etc.
                </AlertDescription>
              </Alert>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-[#1E88E5] transition-colors">
                <Upload className="h-12 w-12 text-[#4A6A7A] mx-auto mb-3" />
                <Input
                  id="assay-upload"
                  type="file"
                  multiple
                  accept=".csv,.tsv,.xlsx"
                  onChange={(e) => handleFileUpload(e, 'assay')}
                  className="hidden"
                />
                <Label htmlFor="assay-upload" className="cursor-pointer">
                  <Button type="button" variant="outline" onClick={() => document.getElementById('assay-upload')?.click()}>
                    Choose Files
                  </Button>
                </Label>
                {projectData.assayFiles.length > 0 && (
                  <div className="mt-3 space-y-1">
                    {projectData.assayFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-center gap-2 text-sm text-[#0B4F8C]">
                        <FileText className="h-4 w-4" />
                        <span>{file.name} ({(file.size / 1024).toFixed(2)} KB)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Geolocation & Timestamp */}
        <Card>
          <CardHeader>
            <CardTitle>Location & Time</CardTitle>
            <CardDescription>Origin and collection details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="latitude">Latitude (Decimal)</Label>
                <Input
                  id="latitude"
                  type="number"
                  step="any"
                  value={projectData.latitude}
                  onChange={(e) => setProjectData({ ...projectData, latitude: e.target.value })}
                  placeholder="e.g., 19.0760"
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="longitude">Longitude (Decimal)</Label>
                <Input
                  id="longitude"
                  type="number"
                  step="any"
                  value={projectData.longitude}
                  onChange={(e) => setProjectData({ ...projectData, longitude: e.target.value })}
                  placeholder="e.g., 72.8777"
                  className="mt-1"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="country">Origin Country</Label>
                <Select value={projectData.country} onValueChange={(value) => setProjectData({ ...projectData, country: value })}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select country" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="india">India</SelectItem>
                    <SelectItem value="usa">United States</SelectItem>
                    <SelectItem value="uk">United Kingdom</SelectItem>
                    <SelectItem value="china">China</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="region">Administrative Region</Label>
                <Input
                  id="region"
                  value={projectData.region}
                  onChange={(e) => setProjectData({ ...projectData, region: e.target.value })}
                  placeholder="e.g., Maharashtra, Mumbai"
                  className="mt-1"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="timestamp">Collection Timestamp (UTC)</Label>
              <Input
                id="timestamp"
                type="datetime-local"
                value={projectData.timestamp}
                onChange={(e) => setProjectData({ ...projectData, timestamp: e.target.value })}
                className="mt-1"
              />
            </div>
          </CardContent>
        </Card>

        {/* Phenotypic/Clinical */}
        <Card>
          <CardHeader>
            <CardTitle>Clinical Information</CardTitle>
            <CardDescription>Symptoms and clinical observations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="symptoms">Symptoms</Label>
              <Textarea
                id="symptoms"
                value={projectData.symptoms}
                onChange={(e) => setProjectData({ ...projectData, symptoms: e.target.value })}
                placeholder="e.g., fever, cough, fatigue, loss of taste/smell"
                className="mt-1"
                rows={2}
              />
            </div>
            <div>
              <Label htmlFor="severity">Clinical Severity</Label>
              <Select value={projectData.severity} onValueChange={(value) => setProjectData({ ...projectData, severity: value })}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select severity level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="asymptomatic">Asymptomatic</SelectItem>
                  <SelectItem value="mild">Mild</SelectItem>
                  <SelectItem value="moderate">Moderate</SelectItem>
                  <SelectItem value="severe">Severe</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="notes">Notes / Provenance</Label>
              <Textarea
                id="notes"
                value={projectData.notes}
                onChange={(e) => setProjectData({ ...projectData, notes: e.target.value })}
                placeholder="Lab notes, collection method, citations, or other relevant information"
                className="mt-1"
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Error Display */}
        {createProject.isError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {createProject.error instanceof Error ? createProject.error.message : 'Failed to create project. Please try again.'}
            </AlertDescription>
          </Alert>
        )}

        {/* Submit */}
        <div className="flex gap-4">
          <Button 
            type="submit" 
            className="flex-1 bg-[#1E88E5] hover:bg-[#0B4F8C]"
            disabled={createProject.isPending || projectData.proteinFiles.length === 0}
          >
            {createProject.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating Project...
              </>
            ) : (
              'Create Project'
            )}
          </Button>
          <Button 
            type="button" 
            variant="outline" 
            onClick={() => navigate('/dashboard/overview')}
            disabled={createProject.isPending}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}