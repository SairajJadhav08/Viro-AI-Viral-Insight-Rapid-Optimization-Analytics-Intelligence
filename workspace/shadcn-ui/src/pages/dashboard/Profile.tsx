import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Mail, Phone, Briefcase, GraduationCap, Award, Github, Linkedin, ExternalLink, Edit, Globe, Loader2, Plus, Trash2, X } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import { useCurrentUser, useUpdateProfile } from '@/hooks/use-auth';
import type { User } from '@/lib/api/auth';
import { toast } from 'sonner';

// Demo user data for fallback with comprehensive profile
const DEMO_USER: User = {
  id: 1,
  email: 'researchuser@example.com',
  first_name: 'Research',
  last_name: 'User',
  phone: '',
  role: 'Researcher',
  qualification: 'Ph.D. in Virology',
  occupation: 'Senior Research Scientist',
  professional_summary: 'To advance the field of computational virology through innovative AI-driven approaches, contributing to the development of next-generation antivirals and improving global pandemic preparedness. Seeking opportunities to lead interdisciplinary research teams and translate computational insights into clinical applications.',
  skills: ['Machine Learning', 'Computational Biology', 'Drug Discovery', 'Viral Genomics'],
  experience: [
    {
      title: 'Senior Research Scientist',
      organization: 'Institute of Computational Biology',
      start_date: '2020',
      end_date: 'Present',
      description: 'Leading research initiatives in AI-driven viral mutation prediction and antiviral drug design.'
    },
    {
      title: 'Postdoctoral Researcher',
      organization: 'Harvard Medical School',
      start_date: '2017',
      end_date: '2020',
      description: 'Conducted research on coronavirus structural biology and therapeutic development.'
    },
    {
      title: 'Research Intern',
      organization: 'NIH - National Institute of Allergy and Infectious Diseases',
      start_date: '2015',
      end_date: '2016',
      description: 'Assisted in viral genomics surveillance and outbreak response projects.'
    }
  ],
  publications: [
    {
      title: 'AI-driven prediction of SARS-CoV-2 mutations and therapeutic targets',
      journal: 'Nature Medicine',
      year: 2024,
      citations: 127
    },
    {
      title: 'Computational approaches to broad-spectrum antiviral development',
      journal: 'Science',
      year: 2023,
      citations: 203
    },
    {
      title: 'Structural dynamics of viral proteins: Implications for drug design',
      journal: 'Cell',
      year: 2022,
      citations: 315
    }
  ],
  awards: [
    {
      title: 'NIH Director\'s New Innovator Award',
      year: 2023,
      organization: 'For groundbreaking work in AI-driven drug discovery'
    },
    {
      title: 'Young Investigator Award',
      year: 2021,
      organization: 'American Society for Virology'
    },
    {
      title: 'Best Paper Award',
      year: 2020,
      organization: 'International Conference on Computational Biology'
    }
  ],
  social_links: {
    github: 'github.com/researchuser',
    linkedin: 'linkedin.com/in/researchuser',
    scholar: 'scholar.google.com/citations?user=researchuser',
    website: 'researchuser.com'
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export default function Profile() {
  const [isEditing, setIsEditing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0); // Force re-render when localStorage changes
  const { data: userData, isLoading, error } = useCurrentUser();
  const updateProfile = useUpdateProfile();

  // Use demo data if API fails, otherwise use real data
  const user: User | null = useMemo((): User | null => {
    if (userData) return userData as User;
    if (error) return DEMO_USER;
    return null;
  }, [userData, error]);

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phone: '',
    qualification: '',
    occupation: '',
    professional_summary: '',
    skills: [] as string[],
    experience: [] as unknown[],
    publications: [] as unknown[],
    awards: [] as unknown[],
    social_links: {} as Record<string, string>,
  });

  // Load form data - prioritize localStorage, then user data, then demo
  useEffect(() => {
    const savedProfile = localStorage.getItem('profile_data');
    let dataSource: User;
    
    if (savedProfile) {
      try {
        const parsed = JSON.parse(savedProfile);
        dataSource = { ...DEMO_USER, ...parsed } as User;
      } catch (e) {
        // If parsing fails, use user data or demo
        dataSource = (user ?? DEMO_USER) as User;
      }
    } else {
      dataSource = (user ?? DEMO_USER) as User;
    }
    
    setFormData({
      firstName: dataSource.first_name || '',
      lastName: dataSource.last_name || '',
      phone: dataSource.phone || '',
      qualification: dataSource.qualification || '',
      occupation: dataSource.occupation || '',
      professional_summary: dataSource.professional_summary || '',
      skills: (dataSource.skills as string[]) || [],
      experience: (dataSource.experience as unknown[]) || [],
      publications: (dataSource.publications as unknown[]) || [],
      awards: (dataSource.awards as unknown[]) || [],
      social_links: (dataSource.social_links as Record<string, string>) || {},
    });
  }, [user]);

  const handleSave = () => {
    const profileData = {
      first_name: formData.firstName,
      last_name: formData.lastName,
      phone: formData.phone,
      qualification: formData.qualification,
      occupation: formData.occupation,
      professional_summary: formData.professional_summary,
      skills: formData.skills,
      experience: formData.experience,
      publications: formData.publications,
      awards: formData.awards,
      social_links: formData.social_links,
    };

    // Save to localStorage immediately for persistence
    const savedUser = user ?? DEMO_USER;
    const updatedUser = {
      ...savedUser,
      ...profileData,
    };
    localStorage.setItem('profile_data', JSON.stringify(updatedUser));
    setRefreshKey(prev => prev + 1); // Trigger re-render to show saved data
    // Dispatch event to notify Header component
    window.dispatchEvent(new CustomEvent('profileUpdated'));

    // Try to save to backend
    updateProfile.mutate(profileData, {
      onSuccess: (data) => {
        // Update localStorage with server response
        if (data) {
          localStorage.setItem('profile_data', JSON.stringify(data));
          setRefreshKey(prev => prev + 1); // Trigger re-render
          window.dispatchEvent(new CustomEvent('profileUpdated'));
        }
        setIsEditing(false);
        toast.success('Profile updated successfully');
      },
      onError: (error: { status?: number }) => {
        // For 404 errors, we've already saved to localStorage, so just close edit mode
        if (error?.status === 404) {
          setIsEditing(false);
          toast.success('Profile saved locally (backend unavailable)');
        }
        // Other errors are handled by the hook
      }
    });
  };

  // Get display user - prioritize saved localStorage data, then user data, then demo
  const displayUser: User = useMemo(() => {
    const savedProfile = localStorage.getItem('profile_data');
    if (savedProfile) {
      try {
        const parsed = JSON.parse(savedProfile);
        return { ...DEMO_USER, ...parsed } as User;
      } catch (e) {
        // If parsing fails, fall through
      }
    }
    return (user ?? DEMO_USER) as User;
  }, [user, refreshKey]);
  const displayName = `${displayUser.first_name || ''} ${displayUser.last_name || ''}`.trim() || 'User';
  const initials = `${displayUser.first_name?.[0] || ''}${displayUser.last_name?.[0] || ''}`.toUpperCase() || 'RU';
  const userRole = displayUser.role || 'Researcher';

  if (isLoading && !user && !error) {
    return (
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[#1E88E5]" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Profile</h1>
        </div>
        <Button 
          onClick={() => isEditing ? handleSave() : setIsEditing(true)} 
          variant="outline"
          disabled={updateProfile.isPending}
        >
          <Edit className="h-4 w-4 mr-2" />
          {isEditing ? (updateProfile.isPending ? 'Saving...' : 'Save Changes') : 'Edit Profile'}
        </Button>
      </div>

      {/* Basic Information */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex flex-col items-center gap-4">
              <Avatar className="h-24 w-24">
                <AvatarImage src={displayUser.avatar_url || undefined} />
                <AvatarFallback className="text-xl bg-primary text-primary-foreground">{initials}</AvatarFallback>
              </Avatar>
              <div className="text-center">
                <h2 className="text-xl font-semibold text-foreground">{displayName}</h2>
                <p className="text-sm text-muted-foreground">{userRole}</p>
              </div>
            </div>

            <div className="flex-1 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">First Name</Label>
                  <Input 
                    id="firstName" 
                    value={isEditing ? formData.firstName : displayUser.first_name || ''} 
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                    disabled={!isEditing} 
                    className="mt-1" 
                  />
                </div>
                <div>
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input 
                    id="lastName" 
                    value={isEditing ? formData.lastName : displayUser.last_name || ''} 
                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                    disabled={!isEditing} 
                    className="mt-1" 
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <Input id="email" type="email" value={displayUser.email} disabled className="bg-muted" />
                  </div>
                </div>
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="phone" 
                      value={isEditing ? formData.phone : displayUser.phone || ''} 
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      disabled={!isEditing} 
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="qualification">Qualification</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <GraduationCap className="h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="qualification" 
                      value={isEditing ? formData.qualification : displayUser.qualification || ''} 
                      onChange={(e) => setFormData({ ...formData, qualification: e.target.value })}
                      disabled={!isEditing}
                      placeholder="e.g., Ph.D. in Virology"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="occupation">Occupation</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <Briefcase className="h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="occupation" 
                      value={isEditing ? formData.occupation : displayUser.occupation || ''} 
                      onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                      disabled={!isEditing}
                      placeholder="e.g., Senior Researcher"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Professional Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Professional Summary</CardTitle>
          <CardDescription>Brief overview of your background and expertise</CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            value={isEditing ? formData.professional_summary : displayUser.professional_summary || ''}
            onChange={(e) => setFormData({ ...formData, professional_summary: e.target.value })}
            disabled={!isEditing}
            rows={4}
            placeholder="Brief overview of your background and expertise"
          />
        </CardContent>
      </Card>

      {/* Experience & Internships */}
      <Card>
        <CardHeader>
          <CardTitle>Experience & Internships</CardTitle>
          <CardDescription>Your professional work history</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.experience && Array.isArray(formData.experience) && formData.experience.length > 0 ? (
            formData.experience.map((exp: any, index: number) => (
              <div key={index} className={`border-l-2 border-primary pl-4 py-2 ${isEditing ? 'border rounded-lg p-4' : ''}`}>
                {isEditing ? (
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 space-y-3">
                        <div>
                          <Label>Title/Position</Label>
                          <Input
                            value={exp.title || exp.position || ''}
                            onChange={(e) => {
                              const newExp = [...formData.experience];
                              newExp[index] = { ...exp, title: e.target.value };
                              setFormData({ ...formData, experience: newExp });
                            }}
                            placeholder="e.g., Senior Research Scientist"
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <Label>Organization/Company</Label>
                          <Input
                            value={exp.organization || exp.company || ''}
                            onChange={(e) => {
                              const newExp = [...formData.experience];
                              newExp[index] = { ...exp, organization: e.target.value };
                              setFormData({ ...formData, experience: newExp });
                            }}
                            placeholder="e.g., Institute of Computational Biology"
                            className="mt-1"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <Label>Start Date</Label>
                            <Input
                              value={exp.start_date || ''}
                              onChange={(e) => {
                                const newExp = [...formData.experience];
                                newExp[index] = { ...exp, start_date: e.target.value };
                                setFormData({ ...formData, experience: newExp });
                              }}
                              placeholder="e.g., 2020"
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label>End Date</Label>
                            <Input
                              value={exp.end_date || ''}
                              onChange={(e) => {
                                const newExp = [...formData.experience];
                                newExp[index] = { ...exp, end_date: e.target.value };
                                setFormData({ ...formData, experience: newExp });
                              }}
                              placeholder="e.g., Present or 2023"
                              className="mt-1"
                            />
                          </div>
                        </div>
                        <div>
                          <Label>Description</Label>
                          <Textarea
                            value={exp.description || ''}
                            onChange={(e) => {
                              const newExp = [...formData.experience];
                              newExp[index] = { ...exp, description: e.target.value };
                              setFormData({ ...formData, experience: newExp });
                            }}
                            placeholder="Describe your role and achievements"
                            className="mt-1"
                            rows={3}
                          />
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          const newExp = formData.experience.filter((_, i) => i !== index);
                          setFormData({ ...formData, experience: newExp });
                        }}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                <h4 className="font-semibold text-foreground">{exp.title || exp.position || 'Experience'}</h4>
                <p className="text-sm text-muted-foreground">
                  {exp.organization || exp.company || ''} {exp.start_date && exp.end_date ? `• ${exp.start_date} - ${exp.end_date}` : exp.period || ''}
                </p>
                {exp.description && (
                  <p className="text-sm mt-2 text-foreground">{exp.description}</p>
                    )}
                  </>
                )}
              </div>
            ))
          ) : (
            !isEditing && <p className="text-sm text-muted-foreground">No experience added yet.</p>
          )}
          {isEditing && (
            <Button
              variant="outline"
              onClick={() => {
                setFormData({
                  ...formData,
                  experience: [...formData.experience, { title: '', organization: '', start_date: '', end_date: '', description: '' }]
                });
              }}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Experience
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Publications & Research Work */}
      <Card>
        <CardHeader>
          <CardTitle>Publications & Research Work</CardTitle>
          <CardDescription>Your published research and academic work</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {formData.publications && Array.isArray(formData.publications) && formData.publications.length > 0 ? (
            formData.publications.map((pub: any, index: number) => (
              <div key={index} className="p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                {isEditing ? (
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 space-y-3">
                        <div>
                          <Label>Title</Label>
                          <Input
                            value={pub.title || pub.name || ''}
                            onChange={(e) => {
                              const newPubs = [...formData.publications];
                              newPubs[index] = { ...pub, title: e.target.value };
                              setFormData({ ...formData, publications: newPubs });
                            }}
                            placeholder="Publication title"
                            className="mt-1"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <Label>Journal/Venue</Label>
                            <Input
                              value={pub.journal || pub.venue || ''}
                              onChange={(e) => {
                                const newPubs = [...formData.publications];
                                newPubs[index] = { ...pub, journal: e.target.value };
                                setFormData({ ...formData, publications: newPubs });
                              }}
                              placeholder="e.g., Nature Medicine"
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label>Year</Label>
                            <Input
                              type="number"
                              value={pub.year || ''}
                              onChange={(e) => {
                                const newPubs = [...formData.publications];
                                newPubs[index] = { ...pub, year: e.target.value ? parseInt(e.target.value) : null };
                                setFormData({ ...formData, publications: newPubs });
                              }}
                              placeholder="e.g., 2024"
                              className="mt-1"
                            />
                          </div>
                        </div>
                        <div>
                          <Label>Citations (optional)</Label>
                          <Input
                            type="number"
                            value={pub.citations || ''}
                            onChange={(e) => {
                              const newPubs = [...formData.publications];
                              newPubs[index] = { ...pub, citations: e.target.value ? parseInt(e.target.value) : null };
                              setFormData({ ...formData, publications: newPubs });
                            }}
                            placeholder="Number of citations"
                            className="mt-1"
                          />
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          const newPubs = formData.publications.filter((_, i) => i !== index);
                          setFormData({ ...formData, publications: newPubs });
                        }}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                <p className="text-sm font-medium text-foreground">
                  {pub.title || pub.name || 'Publication'}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {pub.journal || pub.venue || ''} {pub.year ? `, ${pub.year}` : ''} {pub.citations ? `• Citations: ${pub.citations}` : ''}
                </p>
                  </>
                )}
              </div>
            ))
          ) : (
            !isEditing && <p className="text-sm text-muted-foreground">No publications added yet.</p>
          )}
          {isEditing && (
            <Button
              variant="outline"
              onClick={() => {
                setFormData({
                  ...formData,
                  publications: [...formData.publications, { title: '', journal: '', year: null, citations: null }]
                });
              }}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Publication
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Professional Links & Social Profiles */}
      <Card>
        <CardHeader>
          <CardTitle>Professional Links & Social Profiles</CardTitle>
          <CardDescription>Connect your professional profiles</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-3">
            <Github className="h-5 w-5 text-muted-foreground" />
            <Input 
              value={isEditing ? (formData.social_links?.github || '') : (displayUser.social_links?.github || '')} 
              onChange={(e) => setFormData({ 
                ...formData, 
                social_links: { ...formData.social_links, github: e.target.value } 
              })}
              disabled={!isEditing} 
              placeholder="github.com/username"
              className="flex-1"
            />
            {displayUser.social_links?.github && !isEditing && (
              <Button size="sm" variant="ghost" onClick={() => window.open(`https://${displayUser.social_links?.github}`, '_blank')}>
                <ExternalLink className="h-4 w-4" />
              </Button>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Linkedin className="h-5 w-5 text-muted-foreground" />
            <Input 
              value={isEditing ? (formData.social_links?.linkedin || '') : (displayUser.social_links?.linkedin || '')} 
              onChange={(e) => setFormData({ 
                ...formData, 
                social_links: { ...formData.social_links, linkedin: e.target.value } 
              })}
              disabled={!isEditing} 
              placeholder="linkedin.com/in/username"
              className="flex-1"
            />
            {displayUser.social_links?.linkedin && !isEditing && (
              <Button size="sm" variant="ghost" onClick={() => window.open(`https://${displayUser.social_links?.linkedin}`, '_blank')}>
                <ExternalLink className="h-4 w-4" />
              </Button>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Globe className="h-5 w-5 text-muted-foreground" />
            <Input 
              value={isEditing ? (formData.social_links?.scholar || '') : (displayUser.social_links?.scholar || '')} 
              onChange={(e) => setFormData({ 
                ...formData, 
                social_links: { ...formData.social_links, scholar: e.target.value } 
              })}
              disabled={!isEditing} 
              placeholder="Google Scholar URL"
              className="flex-1"
            />
            {displayUser.social_links?.scholar && !isEditing && (
              <Button size="sm" variant="ghost" onClick={() => window.open(`https://${displayUser.social_links?.scholar}`, '_blank')}>
                <ExternalLink className="h-4 w-4" />
              </Button>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Globe className="h-5 w-5 text-muted-foreground" />
            <Input 
              value={isEditing ? (formData.social_links?.website || '') : (displayUser.social_links?.website || '')} 
              onChange={(e) => setFormData({ 
                ...formData, 
                social_links: { ...formData.social_links, website: e.target.value } 
              })}
              disabled={!isEditing} 
              placeholder="Personal Website"
              className="flex-1"
            />
            {displayUser.social_links?.website && !isEditing && (
              <Button size="sm" variant="ghost" onClick={() => window.open(`https://${displayUser.social_links?.website}`, '_blank')}>
                <ExternalLink className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Career Goals & Objective */}
      <Card>
        <CardHeader>
          <CardTitle>Career Goals & Objective</CardTitle>
          <CardDescription>Your professional aspirations and objectives</CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            value={isEditing ? formData.professional_summary : displayUser.professional_summary || ''}
            onChange={(e) => setFormData({ ...formData, professional_summary: e.target.value })}
            disabled={!isEditing}
            rows={3}
            placeholder="Your career goals and objectives"
          />
        </CardContent>
      </Card>

      {/* Awards & Recognitions */}
      <Card>
        <CardHeader>
          <CardTitle>Awards & Recognitions</CardTitle>
          <CardDescription>Your achievements and honors</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {formData.awards && Array.isArray(formData.awards) && formData.awards.length > 0 ? (
            formData.awards.map((award: any, index: number) => (
              <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                <Award className="h-5 w-5 text-yellow-600 dark:text-yellow-500 mt-0.5 flex-shrink-0" />
                {isEditing ? (
                  <div className="flex-1 space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 space-y-3">
                        <div>
                          <Label>Award Title</Label>
                          <Input
                            value={award.title || award.name || ''}
                            onChange={(e) => {
                              const newAwards = [...formData.awards];
                              newAwards[index] = { ...award, title: e.target.value };
                              setFormData({ ...formData, awards: newAwards });
                            }}
                            placeholder="e.g., NIH Director's New Innovator Award"
                            className="mt-1"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <Label>Year</Label>
                            <Input
                              type="number"
                              value={award.year || ''}
                              onChange={(e) => {
                                const newAwards = [...formData.awards];
                                newAwards[index] = { ...award, year: e.target.value ? parseInt(e.target.value) : null };
                                setFormData({ ...formData, awards: newAwards });
                              }}
                              placeholder="e.g., 2023"
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label>Organization</Label>
                            <Input
                              value={award.organization || award.description || ''}
                              onChange={(e) => {
                                const newAwards = [...formData.awards];
                                newAwards[index] = { ...award, organization: e.target.value };
                                setFormData({ ...formData, awards: newAwards });
                              }}
                              placeholder="Awarding organization"
                              className="mt-1"
                            />
                          </div>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          const newAwards = formData.awards.filter((_, i) => i !== index);
                          setFormData({ ...formData, awards: newAwards });
                        }}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ) : (
                <div className="flex-1">
                  <p className="font-medium text-foreground">{award.title || award.name || 'Award'}</p>
                  <p className="text-sm text-muted-foreground">
                    {award.year ? `${award.year} • ` : ''}{award.organization || award.description || ''}
                  </p>
                </div>
                )}
              </div>
            ))
          ) : (
            !isEditing && <p className="text-sm text-muted-foreground">No awards added yet.</p>
          )}
          {isEditing && (
            <Button
              variant="outline"
              onClick={() => {
                setFormData({
                  ...formData,
                  awards: [...formData.awards, { title: '', year: null, organization: '' }]
                });
              }}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Award
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Skills & Expertise */}
      <Card>
        <CardHeader>
          <CardTitle>Skills & Expertise</CardTitle>
          <CardDescription>Your areas of expertise and skills</CardDescription>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {formData.skills && formData.skills.length > 0 ? (
                  formData.skills.map((skill, index) => (
                    <Badge key={index} variant="secondary" className="flex items-center gap-1">
                      {skill}
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-4 w-4 p-0 hover:bg-destructive/20"
                        onClick={() => {
                          const newSkills = formData.skills.filter((_, i) => i !== index);
                          setFormData({ ...formData, skills: newSkills });
                        }}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No skills added yet.</p>
                )}
              </div>
              <div className="flex gap-2">
                <Input
                  placeholder="Add a skill and press Enter"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                      e.preventDefault();
                      const newSkill = e.currentTarget.value.trim();
                      if (!formData.skills.includes(newSkill)) {
                        setFormData({ ...formData, skills: [...formData.skills, newSkill] });
                      }
                      e.currentTarget.value = '';
                    }
                  }}
                  className="flex-1"
                />
                <Button
                  variant="outline"
                  onClick={(e) => {
                    const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                    if (input && input.value.trim()) {
                      const newSkill = input.value.trim();
                      if (!formData.skills.includes(newSkill)) {
                        setFormData({ ...formData, skills: [...formData.skills, newSkill] });
                      }
                      input.value = '';
                    }
                  }}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ) : (
          <div className="flex flex-wrap gap-2">
            {formData.skills && formData.skills.length > 0 ? (
              formData.skills.map((skill, index) => (
                <Badge key={index} variant="secondary">{skill}</Badge>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No skills added yet.</p>
            )}
          </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}