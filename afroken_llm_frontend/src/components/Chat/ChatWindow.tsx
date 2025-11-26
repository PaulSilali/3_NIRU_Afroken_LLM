import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { useChatStore } from '@/store/chatStore';
import { Message, ServiceType } from '@/types';
import { postChat } from '@/lib/api';
import { toast } from 'sonner';

interface ChatWindowProps {
  initialService?: ServiceType;
}

export function ChatWindow({ initialService }: ChatWindowProps) {
  const { t, i18n } = useTranslation();
  const { messages, isOpen, isTyping, currentService, language, setIsOpen, setIsTyping, addMessage, setCurrentService } = useChatStore();
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (initialService) {
      setCurrentService(initialService);
    }
  }, [initialService, setCurrentService]);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      text,
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await postChat({
        message: text,
        lang: language,
        context: currentService ? { service: currentService } : undefined,
      });

      setIsTyping(false);

      const botMessage: Message = {
        id: response.id,
        role: 'bot',
        text: response.answer,
        citations: response.citations,
        actions: response.actions,
        timestamp: new Date().toISOString(),
      };

      addMessage(botMessage);
    } catch (error) {
      setIsTyping(false);
      toast.error(t('chat.error'));
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
        onClick={() => setIsOpen(false)}
        aria-hidden="true"
      >
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          className="fixed right-0 top-0 h-full w-full sm:w-[500px] bg-background border-l border-border shadow-2xl flex flex-col"
          onClick={(e) => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
          aria-labelledby="chat-title"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border bg-primary text-primary-foreground">
            <div>
              <h2 id="chat-title" className="text-lg font-semibold">
                AfroKen
              </h2>
              <p className="text-xs opacity-90">{t('home.hero.subtitle')}</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              className="text-primary-foreground hover:bg-primary-glow focus-ring"
              aria-label={t('common.close')}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Messages */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-1" role="log" aria-live="polite" aria-label="Chat messages">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">{t('home.services.title')}</p>
                  {currentService && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium">{t(`home.services.${currentService}.title`)}</p>
                      <div className="space-y-1">
                        {(t(`chat.examples.${currentService}`, { returnObjects: true }) as string[]).map(
                          (example: string, index: number) => (
                            <Button
                              key={index}
                              variant="outline"
                              size="sm"
                              className="w-full text-left justify-start text-xs focus-ring"
                              onClick={() => handleSendMessage(example)}
                            >
                              {example}
                            </Button>
                          )
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}

              {isTyping && (
                <div className="flex justify-start mb-4">
                  <div className="bg-botBubble text-botBubble-foreground rounded-2xl px-4 py-3 border border-border">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-current rounded-full typing-dot" />
                      <div className="w-2 h-2 bg-current rounded-full typing-dot" />
                      <div className="w-2 h-2 bg-current rounded-full typing-dot" />
                    </div>
                  </div>
                </div>
              )}

              <div ref={scrollRef} />
            </div>
          </ScrollArea>

          {/* Input */}
          <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
