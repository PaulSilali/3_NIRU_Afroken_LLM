import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { ThumbsUp, ThumbsDown, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { Message } from '@/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { postFeedback } from '@/lib/api';
import { toast } from 'sonner';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const { t } = useTranslation();
  const [showCitations, setShowCitations] = useState(false);
  const [feedback, setFeedback] = useState<'helpful' | 'not_helpful' | null>(null);

  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  const handleFeedback = async (rating: 'helpful' | 'not_helpful') => {
    setFeedback(rating);
    try {
      await postFeedback({
        chatId: 'current-chat',
        messageId: message.id,
        rating,
      });
      toast.success(t('common.save') + 'd');
    } catch (error) {
      toast.error(t('common.error'));
    }
  };

  if (isSystem) {
    return (
      <div className="flex justify-center py-2">
        <p className="text-xs text-muted-foreground">{message.text}</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 message-enter`}
    >
      <div
        className={`max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-userBubble text-userBubble-foreground'
            : 'bg-botBubble text-botBubble-foreground border border-border'
        }`}
        role="article"
        aria-label={`${isUser ? 'Your' : 'AfroKen'} message`}
      >
        {!isUser && (
          <div className="text-xs font-semibold mb-2 text-muted-foreground">AfroKen</div>
        )}

        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>

        {/* Citations */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-border/50">
            <button
              onClick={() => setShowCitations(!showCitations)}
              className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground smooth-transition focus-ring"
              aria-expanded={showCitations}
              aria-controls={`citations-${message.id}`}
            >
              <span className="font-medium">{t('chat.citations')}</span>
              <Badge variant="secondary" className="text-xs">
                {message.citations.length}
              </Badge>
              {showCitations ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </button>

            {showCitations && (
              <div
                id={`citations-${message.id}`}
                className="mt-2 space-y-2"
                role="region"
                aria-label="Source citations"
              >
                {message.citations.map((citation) => (
                  <a
                    key={citation.id}
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-start gap-2 p-2 rounded-lg bg-background/50 hover:bg-background smooth-transition text-xs focus-ring"
                    aria-label={`View source: ${citation.title}`}
                  >
                    <ExternalLink className="w-3 h-3 mt-0.5 flex-shrink-0" aria-hidden="true" />
                    <div className="flex-1">
                      <p className="font-medium">{citation.title}</p>
                      {citation.snippet && (
                        <p className="text-muted-foreground mt-1">{citation.snippet}</p>
                      )}
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        {!isUser && message.actions && message.actions.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.actions.map((action, index) => (
              <Button
                key={index}
                size="sm"
                variant="outline"
                className="text-xs focus-ring"
                onClick={() => toast.info(`Action: ${action.label}`)}
                aria-label={action.label}
              >
                {action.label}
              </Button>
            ))}
          </div>
        )}

        {/* Feedback */}
        {!isUser && (
          <div className="mt-3 pt-3 border-t border-border/50 flex items-center gap-2">
            <span className="text-xs text-muted-foreground">{t('chat.rating.helpful')}?</span>
            <Button
              size="sm"
              variant="ghost"
              className={`h-7 px-2 focus-ring ${
                feedback === 'helpful' ? 'bg-success/10 text-success' : ''
              }`}
              onClick={() => handleFeedback('helpful')}
              disabled={feedback !== null}
              aria-label={t('chat.rating.helpful')}
              aria-pressed={feedback === 'helpful'}
            >
              <ThumbsUp className="w-3 h-3" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className={`h-7 px-2 focus-ring ${
                feedback === 'not_helpful' ? 'bg-destructive/10 text-destructive' : ''
              }`}
              onClick={() => handleFeedback('not_helpful')}
              disabled={feedback !== null}
              aria-label={t('chat.rating.notHelpful')}
              aria-pressed={feedback === 'not_helpful'}
            >
              <ThumbsDown className="w-3 h-3" />
            </Button>
          </div>
        )}

        <div className="text-xs text-muted-foreground/60 mt-2">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </motion.div>
  );
}
