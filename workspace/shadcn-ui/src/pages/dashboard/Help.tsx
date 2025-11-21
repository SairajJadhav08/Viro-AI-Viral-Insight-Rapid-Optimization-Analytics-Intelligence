import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, BookOpen, Video, MessageCircle, Mail } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import ContactForm from '@/components/ContactForm';

export default function Help() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Help & Documentation</h1>
        <p className="text-[#4A6A7A]">Find answers and learn how to use VIRO-AI</p>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#4A6A7A]" />
            <Input placeholder="Search help articles..." className="pl-10" />
          </div>
        </CardContent>
      </Card>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardHeader>
            <BookOpen className="h-8 w-8 text-[#1E88E5] mb-2" />
            <CardTitle className="text-lg">Documentation</CardTitle>
            <CardDescription>Comprehensive guides and API references</CardDescription>
          </CardHeader>
        </Card>
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardHeader>
            <Video className="h-8 w-8 text-[#1E88E5] mb-2" />
            <CardTitle className="text-lg">Video Tutorials</CardTitle>
            <CardDescription>Step-by-step video walkthroughs</CardDescription>
          </CardHeader>
        </Card>
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardHeader>
            <MessageCircle className="h-8 w-8 text-[#1E88E5] mb-2" />
            <CardTitle className="text-lg">Community Forum</CardTitle>
            <CardDescription>Connect with other researchers</CardDescription>
          </CardHeader>
        </Card>
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardHeader>
            <Mail className="h-8 w-8 text-[#1E88E5] mb-2" />
            <CardTitle className="text-lg">Contact Support</CardTitle>
            <CardDescription>Get help from our team</CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* FAQ */}
      <Card>
        <CardHeader>
          <CardTitle>Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="item-1">
              <AccordionTrigger>How do I create a new project?</AccordionTrigger>
              <AccordionContent>
                Click on "New Project" in the sidebar, fill in the project details, upload your viral genome files (FASTA, PDB, or mmCIF formats), and optionally add clinical data in CSV format. Click "Create Project" to start the analysis.
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-2">
              <AccordionTrigger>What file formats are supported?</AccordionTrigger>
              <AccordionContent>
                For protein structures: .fasta, .fa, .pdb, .cif, .mmcif. For clinical data: .csv files with required columns (patient_id, age, onset_date, symptom_codes, lab_results). For experimental assays: .sdf, .mol2 formats.
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-3">
              <AccordionTrigger>How accurate are the predictions?</AccordionTrigger>
              <AccordionContent>
                VIRO-AI predictions have an estimated accuracy of up to 80%, depending on data quality and model assumptions. Results should be used for research guidance only and validated experimentally before clinical or policy actions.
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-4">
              <AccordionTrigger>What is the Deadliness Score?</AccordionTrigger>
              <AccordionContent>
                The Deadliness Score (0-100) is a proprietary metric that quantifies the potential danger of a viral variant based on R₀ impact, binding affinity, immune evasion signals, and cytopathic effect indices.
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-5">
              <AccordionTrigger>How can I export my results?</AccordionTrigger>
              <AccordionContent>
                On the Results page, click the "Export Report" button to download a comprehensive PDF report with all visualizations and data. You can also download individual structure files, CSV tables, and raw model outputs.
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>

      {/* Contact Support Form */}
      <ContactForm 
        formspreeId="YOUR_FORMSPREE_ID" 
        className="mt-6"
      />
      
      {/* Additional Contact Info */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Other Ways to Reach Us</CardTitle>
          <CardDescription>Alternative contact methods</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-[#4A6A7A]">
              For urgent matters or if you prefer other contact methods:
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-[#1E88E5]" />
                <span className="text-sm">Email: support@viro-ai.com</span>
              </div>
              <p className="text-xs text-[#4A6A7A] mt-2">
                All form submissions are automatically forwarded to our official support email.
                You will receive responses at the email address you provide in the form above.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}