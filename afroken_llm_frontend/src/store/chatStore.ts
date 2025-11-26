import { create } from 'zustand';
import { Message, Language, ServiceType } from '@/types';

interface ChatState {
  messages: Message[];
  isOpen: boolean;
  isTyping: boolean;
  currentService?: ServiceType;
  language: Language;
  
  setIsOpen: (isOpen: boolean) => void;
  setIsTyping: (isTyping: boolean) => void;
  setCurrentService: (service?: ServiceType) => void;
  setLanguage: (language: Language) => void;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isOpen: false,
  isTyping: false,
  currentService: undefined,
  language: (localStorage.getItem('language') as Language) || 'en',
  
  setIsOpen: (isOpen) => set({ isOpen }),
  setIsTyping: (isTyping) => set({ isTyping }),
  setCurrentService: (currentService) => set({ currentService }),
  setLanguage: (language) => {
    localStorage.setItem('language', language);
    set({ language });
  },
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  clearMessages: () => set({ messages: [] }),
}));
