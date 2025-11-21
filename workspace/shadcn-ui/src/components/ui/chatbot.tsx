import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageCircle, X, Send, Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m VIRO-AI Assistant. I\'m here to help you with any questions about the platform, virology research, or how to use our tools. How can I assist you today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate bot response
    setTimeout(() => {
      const botResponse = generateBotResponse(inputValue);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponse,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000);
  };

  const generateBotResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.includes('how') && (lowerQuery.includes('use') || lowerQuery.includes('start'))) {
      return 'To get started with VIRO-AI:\n\n1. Navigate to "New Project" to create a new analysis\n2. Upload your viral sequence data or select from our database\n3. Choose your analysis type (genomic surveillance, protein modeling, or drug design)\n4. Review results in the Results section\n\nWould you like more details on any specific feature?';
    }

    if (lowerQuery.includes('upload') || lowerQuery.includes('data')) {
      return 'VIRO-AI accepts various data formats:\n\n• FASTA files for genomic sequences\n• PDB files for protein structures\n• CSV/Excel for epidemiological data\n\nYou can upload files up to 100MB. For larger datasets, please contact our support team.';
    }

    if (lowerQuery.includes('result') || lowerQuery.includes('analysis')) {
      return 'Your analysis results include:\n\n• Mutation predictions with confidence scores\n• Protein structure visualizations\n• Drug binding affinity predictions\n• Downloadable reports in PDF/CSV format\n\nYou can access all past results in the History section.';
    }

    if (lowerQuery.includes('protein') || lowerQuery.includes('structure')) {
      return 'Our protein modeling feature uses AlphaFold-based algorithms to:\n\n• Predict 3D structures from sequences\n• Identify binding sites\n• Simulate protein-drug interactions\n• Generate structure quality metrics\n\nWould you like to know more about any specific aspect?';
    }

    if (lowerQuery.includes('drug') || lowerQuery.includes('design')) {
      return 'The generative drug design module:\n\n• Suggests novel antiviral compounds\n• Optimizes existing molecules\n• Predicts ADMET properties\n• Ranks candidates by efficacy\n\nYou can export results for further experimental validation.';
    }

    if (lowerQuery.includes('outbreak') || lowerQuery.includes('forecast')) {
      return 'Our epidemiological forecasting uses:\n\n• Real-time surveillance data\n• Machine learning models\n• Geographic spread predictions\n• Risk assessment scores\n\nYou can customize parameters for different scenarios.';
    }

    if (lowerQuery.includes('help') || lowerQuery.includes('support')) {
      return 'I\'m here to help! You can:\n\n• Ask me about platform features\n• Get guidance on data formats\n• Learn about analysis workflows\n• Access documentation links\n\nFor technical issues, visit the Help section or contact support@viro-ai.com';
    }

    if (lowerQuery.includes('account') || lowerQuery.includes('profile')) {
      return 'To manage your account:\n\n• Go to Profile to update personal information\n• Visit Settings for preferences and notifications\n• Check your usage and credits in Overview\n• Manage team members in Settings (for institutional accounts)';
    }

    // Default response
    return 'I understand you\'re asking about "' + query + '". Could you please provide more details? I can help with:\n\n• Platform navigation and features\n• Data upload and formats\n• Analysis workflows\n• Results interpretation\n• Account management\n\nFeel free to ask specific questions!';
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg bg-[#1E88E5] hover:bg-[#0B4F8C] z-50"
          size="icon"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <Card className="fixed bottom-6 right-6 w-96 h-[600px] shadow-2xl z-50 flex flex-col">
          <CardHeader className="bg-gradient-to-r from-[#0B4F8C] to-[#1E88E5] text-white rounded-t-lg flex flex-row items-center justify-between py-4">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <CardTitle className="text-lg">VIRO-AI Assistant</CardTitle>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white/20 h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-0">
            {/* Messages Area */}
            <ScrollArea className="flex-1 p-4" ref={scrollRef}>
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      'flex gap-2',
                      message.sender === 'user' ? 'justify-end' : 'justify-start'
                    )}
                  >
                    {message.sender === 'bot' && (
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-[#1E88E5] flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                    )}
                    <div
                      className={cn(
                        'max-w-[75%] rounded-lg px-4 py-2 whitespace-pre-line',
                        message.sender === 'user'
                          ? 'bg-[#1E88E5] text-white'
                          : 'bg-gray-100 text-[#0B2336]'
                      )}
                    >
                      <p className="text-sm">{message.text}</p>
                      <p className="text-xs mt-1 opacity-70">
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    {message.sender === 'user' && (
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-[#4A6A7A] flex items-center justify-center">
                        <User className="h-4 w-4 text-white" />
                      </div>
                    )}
                  </div>
                ))}
                {isTyping && (
                  <div className="flex gap-2 justify-start">
                    <div className="flex-shrink-0 h-8 w-8 rounded-full bg-[#1E88E5] flex items-center justify-center">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-[#4A6A7A] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-[#4A6A7A] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-[#4A6A7A] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Type your question..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="flex-1"
                />
                <Button
                  onClick={handleSend}
                  disabled={!inputValue.trim() || isTyping}
                  className="bg-[#1E88E5] hover:bg-[#0B4F8C]"
                  size="icon"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-[#4A6A7A] mt-2">
                Ask me anything about VIRO-AI platform features and workflows
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
}