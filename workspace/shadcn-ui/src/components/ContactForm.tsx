/**
 * Contact Form Component with Formspree Integration
 * Submits form data to Formspree which sends emails to your official email
 */

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Mail, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

interface ContactFormProps {
  formspreeId?: string; // Your Formspree form ID (e.g., "xvgwqkny")
  defaultEmail?: string; // Pre-fill email if user is logged in
  className?: string;
}

export default function ContactForm({ 
  formspreeId = 'YOUR_FORMSPREE_ID', // Replace with your actual Formspree form ID
  defaultEmail = '',
  className = ''
}: ContactFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: defaultEmail,
    subject: '',
    message: '',
    projectId: '' // Optional: if contacting about a specific project
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      // Submit to Formspree
      const response = await fetch(`https://formspree.io/f/${formspreeId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          subject: formData.subject,
          message: formData.message,
          projectId: formData.projectId || undefined,
          _replyto: formData.email, // This sets the reply-to email
        })
      });

      if (response.ok) {
        setSubmitStatus('success');
        toast.success('Message sent successfully! We will respond to your email soon.');
        // Reset form
        setFormData({
          name: '',
          email: defaultEmail,
          subject: '',
          message: '',
          projectId: ''
        });
      } else {
        const error = await response.json();
        throw new Error(error.error || 'Failed to send message');
      }
    } catch (error: any) {
      setSubmitStatus('error');
      toast.error(error.message || 'Failed to send message. Please try again.');
      console.error('Formspree error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Mail className="h-5 w-5 text-[#1E88E5]" />
          Contact Support
        </CardTitle>
        <CardDescription>
          Send us a message and we'll respond to your official email address
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <Label htmlFor="name">Your Name *</Label>
            <Input
              id="name"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="John Doe"
              className="mt-1"
              disabled={isSubmitting}
            />
          </div>

          {/* Email */}
          <div>
            <Label htmlFor="email">Your Email *</Label>
            <Input
              id="email"
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="your.email@example.com"
              className="mt-1"
              disabled={isSubmitting}
            />
            <p className="text-xs text-[#4A6A7A] mt-1">
              We'll send our response to this email address
            </p>
          </div>

          {/* Subject */}
          <div>
            <Label htmlFor="subject">Subject *</Label>
            <Input
              id="subject"
              required
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              placeholder="e.g., Technical Support, Project Inquiry"
              className="mt-1"
              disabled={isSubmitting}
            />
          </div>

          {/* Project ID (Optional) */}
          <div>
            <Label htmlFor="projectId">Project ID (Optional)</Label>
            <Input
              id="projectId"
              type="number"
              value={formData.projectId}
              onChange={(e) => setFormData({ ...formData, projectId: e.target.value })}
              placeholder="If contacting about a specific project"
              className="mt-1"
              disabled={isSubmitting}
            />
          </div>

          {/* Message */}
          <div>
            <Label htmlFor="message">Message *</Label>
            <Textarea
              id="message"
              required
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              placeholder="Please describe your question or issue in detail..."
              rows={6}
              className="mt-1"
              disabled={isSubmitting}
            />
          </div>

          {/* Status Messages */}
          {submitStatus === 'success' && (
            <Alert className="border-green-300 bg-green-50">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                Message sent successfully! Check your email for our response.
              </AlertDescription>
            </Alert>
          )}

          {submitStatus === 'error' && (
            <Alert className="border-red-300 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                Failed to send message. Please check your connection and try again.
              </AlertDescription>
            </Alert>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full bg-[#1E88E5] hover:bg-[#0B4F8C]"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Mail className="h-4 w-4 mr-2" />
                Send Message
              </>
            )}
          </Button>

          <p className="text-xs text-center text-[#4A6A7A]">
            By submitting this form, you agree to receive responses at the email address provided.
          </p>
        </form>
      </CardContent>
    </Card>
  );
}

