import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Shield, TrendingUp, Zap, Database, Activity, DollarSign, Dna, Microscope, FlaskConical, Brain, Sparkles, BarChart3, Mail, Phone } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Index() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    organization: '',
    email: '',
    role: '',
    message: ''
  });

  const problems = [
    {
      icon: TrendingUp,
      title: 'Unpredictable Viral Mutations',
      description: 'Viruses evolve rapidly, so VIRO-AI predicts future mutations before they appear.',
      color: 'text-red-600'
    },
    {
      icon: Zap,
      title: 'Slow Drug & Vaccine Development',
      description: 'Traditional development is too slow, so VIRO-AI accelerates antidote discovery using AI models.',
      color: 'text-orange-600'
    },
    {
      icon: Shield,
      title: 'Clinical Trial Risk & Ethical Issues',
      description: 'Early human testing is dangerous, so VIRO-AI simulates drug effects virtually to reduce fatalities.',
      color: 'text-green-600'
    },
    {
      icon: Database,
      title: 'Fragmented Genomic & Clinical Data',
      description: 'Biological data is scattered, so VIRO-AI integrates all datasets into a unified computational pipeline.',
      color: 'text-purple-600'
    },
    {
      icon: Activity,
      title: 'Poor Outbreak Forecasting',
      description: 'Current systems react late, so VIRO-AI predicts outbreaks using mutation-aware epidemiological models.',
      color: 'text-yellow-600'
    },
    {
      icon: DollarSign,
      title: 'High Cost & Low Accessibility of Bioinformatics',
      description: 'Advanced simulations need expensive infrastructure, so VIRO-AI provides scalable GPU-cloud access.',
      color: 'text-cyan-600'
    }
  ];

  const processSteps = [
    {
      icon: Database,
      title: 'Data Input & Upload',
      description: 'Users upload viral genomes, protein structures, or clinical datasets through a secure portal.',
      color: 'bg-blue-50 border-blue-200'
    },
    {
      icon: Brain,
      title: 'AI Processing & Mutation Prediction',
      description: 'The engine analyzes sequences, predicts future mutations, and models structural changes.',
      color: 'bg-purple-50 border-purple-200'
    },
    {
      icon: FlaskConical,
      title: 'Drug Generation & Optimization',
      description: 'Generative AI designs antidotes and optimizes molecules using docking and QM/MM refinement.',
      color: 'bg-green-50 border-green-200'
    },
    {
      icon: Microscope,
      title: 'Clinical Simulation & Risk Scoring',
      description: 'In-silico models simulate drug effects, toxicity, and compute the Deadliness Score for each variant.',
      color: 'bg-orange-50 border-orange-200'
    },
    {
      icon: BarChart3,
      title: 'Interactive Dashboard Output',
      description: 'Results appear through 3D visualizations, outbreak forecasts, and ranked antidote candidates.',
      color: 'bg-cyan-50 border-cyan-200'
    }
  ];

  const features = [
    {
      icon: TrendingUp,
      title: 'Predictive Viral Mutation Forecasting',
      description: 'AI models forecast future mutations before they appear in real-world surveillance.',
      color: 'text-blue-600'
    },
    {
      icon: Shield,
      title: 'Deadliness & Pathogenicity Scoring',
      description: 'A proprietary score quantifies how dangerous each predicted mutation could become.',
      color: 'text-red-600'
    },
    {
      icon: Sparkles,
      title: 'AI-Driven Drug & Antidote Generation',
      description: 'Generative models design new antiviral molecules and antibodies in minutes.',
      color: 'text-purple-600'
    },
    {
      icon: FlaskConical,
      title: 'Smart Chemical Optimization of Lead Drugs',
      description: 'QM/MM simulations suggest precise chemical tweaks to boost drug potency and safety.',
      color: 'text-green-600'
    },
    {
      icon: Microscope,
      title: 'In-Silico Clinical Trial Simulator',
      description: 'Digital-twin models simulate drug effects, toxicity, and immune responses without human risk.',
      color: 'text-orange-600'
    },
    {
      icon: Activity,
      title: 'Symptom & Preventive Measure Prediction',
      description: 'Maps mutations to clinical outcomes and suggests tailored preventive strategies.',
      color: 'text-cyan-600'
    },
    {
      icon: Dna,
      title: '3D Molecular Visualization Engine',
      description: 'Interactive GPU-rendered interface for protein folding, docking, and molecular interactions.',
      color: 'text-indigo-600'
    },
    {
      icon: BarChart3,
      title: 'Real-Time Outbreak Forecasting',
      description: 'SEIR + AI-enhanced epidemiology predicts spread patterns and issues early alerts.',
      color: 'text-pink-600'
    }
  ];

  const teamMembers = [
    {
      name: 'Sairaj Jadhav',
      email: 'sairajjadhav433@gmail.com',
      phone: '+91 935 686 0010'
    },
    {
      name: 'Vedant Lanjekar',
      email: 'vedantlanjekar456@gmail.com',
      phone: '+91 9076027036'
    },
    {
      name: 'Mrigyisha Sawant',
      email: 'mrigyishasawant@gmail.com',
      phone: '+91 788 768 1402'
    },
    {
      name: 'Yash Wase',
      email: 'yashwase13@gmail.com',
      phone: '+91 749 948 9664'
    }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    alert('Thank you for your interest! We will contact you soon.');
  };

  const scrollToContact = () => {
    const contactSection = document.getElementById('contact-section');
    if (contactSection) {
      contactSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-[#EAF3FF]">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Dna className="h-8 w-8 text-[#0B4F8C]" />
            <span className="text-2xl font-bold text-[#0B2336]">VIRO-AI</span>
          </div>
          <Button onClick={() => navigate('/login')} className="bg-[#1E88E5] hover:bg-[#0B4F8C]">
            Sign In
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center bg-[#F0F8FF]">
        <h1 className="text-6xl font-bold text-[#0B2336] mb-6">
          VIRO-AI
        </h1>
        <h2 className="text-3xl font-semibold text-[#0B4F8C] mb-8">
          Viral Insight & Rapid Optimization – Analytics Intelligence
        </h2>
        <p className="text-lg text-[#4A6A7A] max-w-4xl mx-auto leading-relaxed mb-8">
          VIRO-AI is a cloud-native computational virology platform that unifies genomic surveillance, protein modeling, generative drug design, and epidemiological forecasting. It converts viral sequence data into actionable insights to accelerate antivirals, guide public-health response, and support research workflows.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
          <Button 
            onClick={() => navigate('/login')} 
            size="lg"
            className="bg-[#1E88E5] hover:bg-[#0B4F8C] text-white font-semibold px-8 py-6 text-lg"
          >
            SIGN IN
          </Button>
          <Button 
            onClick={scrollToContact}
            size="lg"
            className="bg-[#1E88E5] hover:bg-[#0B4F8C] text-white font-semibold px-8 py-6 text-lg"
          >
            GET DEMO
          </Button>
        </div>
      </section>

      {/* Problems We Solve */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-4xl font-bold text-center text-[#0B2336] mb-12">
          Problems We Solve
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {problems.map((problem, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow border-l-4 border-l-[#1E88E5]">
              <CardHeader>
                <problem.icon className={`h-12 w-12 ${problem.color} mb-4`} />
                <CardTitle className="text-[#0B2336]">{problem.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[#4A6A7A]">{problem.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* How Our System Works */}
      <section className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center text-[#0B2336] mb-4">
            How Our System Works
          </h2>
          <p className="text-center text-[#4A6A7A] mb-12 text-lg">
            A streamlined 5-step workflow from data input to actionable insights
          </p>
          
          {/* Workflow Cards */}
          <div className="relative max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
              {processSteps.map((step, index) => (
                <div key={index} className="relative">
                  <Card className={`${step.color} border-2 hover:shadow-xl transition-all duration-300 h-full`}>
                    <CardHeader className="text-center pb-3">
                      <div className="mx-auto w-16 h-16 rounded-full bg-gradient-to-br from-[#1E88E5] to-[#0B4F8C] flex items-center justify-center mb-3 shadow-lg">
                        <span className="text-2xl font-bold text-white">{index + 1}</span>
                      </div>
                      <div className="mx-auto w-14 h-14 rounded-full bg-white flex items-center justify-center mb-3 shadow-md">
                        <step.icon className="h-7 w-7 text-[#0B4F8C]" />
                      </div>
                      <CardTitle className="text-base text-[#0B2336] leading-tight">
                        {step.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-center pt-0">
                      <p className="text-xs text-[#4A6A7A] leading-relaxed">
                        {step.description}
                      </p>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          </div>

          {/* Workflow Summary */}
          <div className="mt-12 max-w-4xl mx-auto">
            <Card className="bg-gradient-to-r from-[#EAF3FF] to-[#E3F2FD] border-2 border-[#1E88E5]">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#1E88E5] flex items-center justify-center">
                    <Sparkles className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-[#0B2336] mb-2">End-to-End Workflow</h3>
                    <p className="text-[#4A6A7A]">
                      From raw viral data to actionable intelligence, VIRO-AI's automated pipeline processes your inputs through advanced AI models, generates optimized drug candidates, simulates clinical outcomes, and delivers comprehensive visualizations—all in a unified, cloud-native platform designed for speed and accuracy.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-4xl font-bold text-center text-[#0B2336] mb-12">
          Key Features & USPs
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <feature.icon className={`h-10 w-10 ${feature.color} mb-3`} />
                <CardTitle className="text-[#0B2336] text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-[#4A6A7A]">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact-section" className="bg-[#0B2336] py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center text-white mb-12">
            Contact Us
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Contact Form */}
            <Card className="bg-white">
              <CardHeader>
                <CardTitle className="text-[#0B2336]">Request a Demo</CardTitle>
                <CardDescription>Fill out the form and we'll get back to you soon</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="name">Name *</Label>
                    <Input
                      id="name"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="organization">Organization *</Label>
                    <Input
                      id="organization"
                      required
                      value={formData.organization}
                      onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="role">Role *</Label>
                    <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select your role" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="researcher">Researcher</SelectItem>
                        <SelectItem value="clinician">Clinician</SelectItem>
                        <SelectItem value="data-scientist">Data Scientist</SelectItem>
                        <SelectItem value="pharma">Pharma Partner</SelectItem>
                        <SelectItem value="government">Government</SelectItem>
                        <SelectItem value="student">Student</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="message">Message *</Label>
                    <Textarea
                      id="message"
                      required
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      className="mt-1"
                      rows={4}
                    />
                  </div>
                  <p className="text-xs text-[#4A6A7A]">
                    For institutional or government access, please indicate 'Gov't / Institutional' in message.
                  </p>
                  <Button type="submit" className="w-full bg-[#1E88E5] hover:bg-[#0B4F8C]">
                    Request a Demo
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Team Information */}
            <div className="text-white">
              <h3 className="text-2xl font-bold mb-6">Our Team</h3>
              <div className="space-y-6">
                {teamMembers.map((member, index) => (
                  <Card key={index} className="bg-white/10 backdrop-blur-sm border-white/20">
                    <CardContent className="pt-6">
                      <h4 className="text-xl font-semibold text-white mb-3">{member.name}</h4>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-white/90">
                          <Mail className="h-4 w-4" />
                          <a href={`mailto:${member.email}`} className="hover:text-[#1E88E5] transition-colors">
                            {member.email}
                          </a>
                        </div>
                        <div className="flex items-center gap-2 text-white/90">
                          <Phone className="h-4 w-4" />
                          <a href={`tel:${member.phone}`} className="hover:text-[#1E88E5] transition-colors">
                            {member.phone}
                          </a>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0B2336] border-t border-white/10 py-8">
        <div className="container mx-auto px-4 text-center text-white/70">
          <p>&copy; 2025 VIRO-AI. All rights reserved.</p>
          <p className="mt-2 text-sm">Predictive Virology • Antidote Design • Outbreak Forecasting</p>
        </div>
      </footer>
    </div>
  );
}