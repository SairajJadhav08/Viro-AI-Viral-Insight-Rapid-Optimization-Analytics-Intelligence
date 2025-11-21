import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dna } from 'lucide-react';
import { useSignIn, useSignUp } from '@/hooks/use-auth';
import { toast } from 'sonner';

export default function Login() {
  const [signInData, setSignInData] = useState({ email: '', password: '', remember: false });
  const [signUpData, setSignUpData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: '',
    password: '',
    confirmPassword: '',
    agreedToTerms: false
  });

  const signInMutation = useSignIn();
  const signUpMutation = useSignUp();

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    signInMutation.mutate({
      email: signInData.email,
      password: signInData.password,
      remember: signInData.remember,
    });
  };

  const handleSignUp = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate password match
    if (signUpData.password !== signUpData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    
    // Validate terms agreement
    if (!signUpData.agreedToTerms) {
      toast.error('Please agree to the Terms & Privacy Policy');
      return;
    }
    
    // Validate required fields
    if (!signUpData.firstName || !signUpData.lastName || !signUpData.email || !signUpData.role) {
      toast.error('Please fill in all required fields');
      return;
    }
    
    signUpMutation.mutate({
      firstName: signUpData.firstName,
      lastName: signUpData.lastName,
      email: signUpData.email,
      phone: signUpData.phone || undefined,
      role: signUpData.role,
      password: signUpData.password,
      confirmPassword: signUpData.confirmPassword,
    });
  };

  const getPasswordStrength = (password: string) => {
    if (password.length === 0) return { strength: 0, label: '', color: '' };
    if (password.length < 8) return { strength: 33, label: 'Weak', color: 'bg-red-500' };
    if (password.length < 12) return { strength: 66, label: 'Medium', color: 'bg-yellow-500' };
    return { strength: 100, label: 'Strong', color: 'bg-green-500' };
  };

  const passwordStrength = getPasswordStrength(signUpData.password);

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Auth Form (30%) */}
      <div className="w-full lg:w-[30%] flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-2 mb-8 justify-center lg:justify-start">
            <Dna className="h-8 w-8 text-[#0B4F8C]" />
            <span className="text-2xl font-bold text-[#0B2336]">VIRO-AI</span>
          </div>

          <Tabs defaultValue="signin" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="signin">Sign In</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>

            {/* Sign In Tab */}
            <TabsContent value="signin">
              <Card>
                <CardHeader>
                  <CardTitle>Welcome Back</CardTitle>
                  <CardDescription>Use institutional email for research accounts.</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSignIn} className="space-y-4">
                    <div>
                      <Label htmlFor="signin-email">Email address</Label>
                      <Input
                        id="signin-email"
                        type="email"
                        required
                        value={signInData.email}
                        onChange={(e) => setSignInData({ ...signInData, email: e.target.value })}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="signin-password">Password</Label>
                      <Input
                        id="signin-password"
                        type="password"
                        required
                        value={signInData.password}
                        onChange={(e) => setSignInData({ ...signInData, password: e.target.value })}
                        className="mt-1"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="remember"
                          checked={signInData.remember}
                          onCheckedChange={(checked) => setSignInData({ ...signInData, remember: checked as boolean })}
                        />
                        <Label htmlFor="remember" className="text-sm font-normal cursor-pointer">
                          Remember me
                        </Label>
                      </div>
                      <Button variant="link" className="px-0 text-[#1E88E5]">
                        Forgot password?
                      </Button>
                    </div>
                    <Button 
                      type="submit" 
                      className="w-full bg-[#1E88E5] hover:bg-[#0B4F8C]"
                      disabled={signInMutation.isPending}
                    >
                      {signInMutation.isPending ? 'Signing in...' : 'Sign In'}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Sign Up Tab */}
            <TabsContent value="signup">
              <Card>
                <CardHeader>
                  <CardTitle>Create Account</CardTitle>
                  <CardDescription>Join the VIRO-AI research community</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSignUp} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="firstName">First Name *</Label>
                        <Input
                          id="firstName"
                          required
                          value={signUpData.firstName}
                          onChange={(e) => setSignUpData({ ...signUpData, firstName: e.target.value })}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="lastName">Last Name *</Label>
                        <Input
                          id="lastName"
                          required
                          value={signUpData.lastName}
                          onChange={(e) => setSignUpData({ ...signUpData, lastName: e.target.value })}
                          className="mt-1"
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="signup-email">Email address *</Label>
                      <Input
                        id="signup-email"
                        type="email"
                        required
                        value={signUpData.email}
                        onChange={(e) => setSignUpData({ ...signUpData, email: e.target.value })}
                        className="mt-1"
                      />
                      <p className="text-xs text-[#4A6A7A] mt-1">Prefer institutional email for research accounts</p>
                    </div>
                    <div>
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input
                        id="phone"
                        type="tel"
                        value={signUpData.phone}
                        onChange={(e) => setSignUpData({ ...signUpData, phone: e.target.value })}
                        className="mt-1"
                        placeholder="E.164 format (e.g., +1234567890)"
                      />
                    </div>
                    <div>
                      <Label htmlFor="role">Role *</Label>
                      <Select value={signUpData.role} onValueChange={(value) => setSignUpData({ ...signUpData, role: value })}>
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
                      <Label htmlFor="signup-password">Password *</Label>
                      <Input
                        id="signup-password"
                        type="password"
                        required
                        value={signUpData.password}
                        onChange={(e) => setSignUpData({ ...signUpData, password: e.target.value })}
                        className="mt-1"
                      />
                      {signUpData.password && (
                        <div className="mt-2">
                          <div className="flex items-center gap-2 mb-1">
                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${passwordStrength.color} transition-all`}
                                style={{ width: `${passwordStrength.strength}%` }}
                              />
                            </div>
                            <span className="text-xs text-[#4A6A7A]">{passwordStrength.label}</span>
                          </div>
                          <p className="text-xs text-[#4A6A7A]">Min 12 characters recommended</p>
                        </div>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="confirmPassword">Confirm Password *</Label>
                      <Input
                        id="confirmPassword"
                        type="password"
                        required
                        value={signUpData.confirmPassword}
                        onChange={(e) => setSignUpData({ ...signUpData, confirmPassword: e.target.value })}
                        className="mt-1"
                      />
                    </div>
                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="terms"
                        checked={signUpData.agreedToTerms}
                        onCheckedChange={(checked) => setSignUpData({ ...signUpData, agreedToTerms: checked as boolean })}
                      />
                      <Label htmlFor="terms" className="text-sm font-normal cursor-pointer leading-relaxed">
                        I agree to VIRO-AI{' '}
                        <Button variant="link" className="p-0 h-auto text-[#1E88E5]">
                          Terms & Privacy Policy
                        </Button>
                      </Label>
                    </div>
                    <Button 
                      type="submit" 
                      className="w-full bg-[#1E88E5] hover:bg-[#0B4F8C]"
                      disabled={signUpMutation.isPending}
                    >
                      {signUpMutation.isPending ? 'Creating account...' : 'Create Account'}
                    </Button>
                    <p className="text-xs text-[#4A6A7A] text-center">
                      Your data remains private and used only for research & system improvements per our policy.
                    </p>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Right Side - Branding Panel (70%) */}
      <div className="hidden lg:flex lg:w-[70%] bg-gradient-to-br from-[#0B4F8C] via-[#1E88E5] to-[#0B4F8C] items-center justify-center p-12">
        <div className="text-center text-white space-y-6">
          <Dna className="h-24 w-24 mx-auto mb-8" />
          <h1 className="text-6xl font-bold">VIRO-AI</h1>
          <p className="text-2xl font-light">
            Predictive Virology • Antidote Design • Outbreak Forecasting
          </p>
          <div className="mt-12 space-y-4 text-lg">
            <p className="flex items-center justify-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full"></span>
              AI-Powered Viral Mutation Prediction
            </p>
            <p className="flex items-center justify-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full"></span>
              Generative Drug Design & Optimization
            </p>
            <p className="flex items-center justify-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full"></span>
              Real-Time Outbreak Forecasting
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}