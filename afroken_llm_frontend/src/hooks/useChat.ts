import { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { postChat } from '@/lib/api';
import { useChatStore } from '@/store/chatStore';
import { Message } from '@/types';
import { toast } from 'sonner';

export function useChat() {
  const { messages, language, currentService, addMessage, setIsTyping } = useChatStore();

  const chatMutation = useMutation({
    mutationFn: postChat,
    onMutate: () => {
      setIsTyping(true);
    },
    onSuccess: (response) => {
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
    },
    onError: () => {
      setIsTyping(false);
      toast.error('Failed to send message. Please try again.');
    },
  });

  const sendMessage = useCallback(
    (text: string) => {
      const userMessage: Message = {
        id: `msg_${Date.now()}`,
        role: 'user',
        text,
        timestamp: new Date().toISOString(),
      };

      addMessage(userMessage);

      chatMutation.mutate({
        message: text,
        lang: language,
        context: currentService ? { service: currentService } : undefined,
      });
    },
    [language, currentService, addMessage, chatMutation]
  );

  return {
    messages,
    sendMessage,
    isLoading: chatMutation.isPending,
  };
}
