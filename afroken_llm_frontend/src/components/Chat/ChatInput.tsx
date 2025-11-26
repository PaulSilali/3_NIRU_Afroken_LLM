import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Send, Mic } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const { t } = useTranslation();
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (!message.trim()) return;
    onSend(message.trim());
    setMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice input is not supported in your browser');
      return;
    }

    setIsRecording(!isRecording);
    
    if (!isRecording) {
      toast.info('Voice input: Click mic again to stop');
      // In a real app, implement Web Speech API here
    } else {
      toast.info('Voice input stopped');
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
  };

  return (
    <div className="border-t border-border bg-background p-4">
      <div className="flex gap-2 items-end">
        <div className="flex-1 relative">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder={t('chat.input.placeholder')}
            disabled={disabled}
            className="min-h-[44px] max-h-[150px] resize-none pr-12 focus-ring"
            rows={1}
            aria-label={t('chat.input.placeholder')}
          />
          <Button
            type="button"
            size="sm"
            variant="ghost"
            className={`absolute right-2 bottom-2 h-8 w-8 p-0 focus-ring ${
              isRecording ? 'text-destructive' : ''
            }`}
            onClick={handleVoiceInput}
            disabled={disabled}
            aria-label={t('chat.input.voiceInput')}
            aria-pressed={isRecording}
          >
            <Mic className={`h-4 w-4 ${isRecording ? 'animate-pulse' : ''}`} />
          </Button>
        </div>

        <Button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          size="icon"
          className="h-11 w-11 flex-shrink-0 focus-ring"
          aria-label={t('chat.input.send')}
        >
          <Send className="h-5 w-5" aria-hidden="true" />
        </Button>
      </div>

      <p className="text-xs text-muted-foreground mt-2 px-1">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
