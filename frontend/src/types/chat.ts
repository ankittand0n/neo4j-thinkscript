export type AIModel = 'gpt-3.5-turbo' | 'gpt-4-turbo-preview' | 'claude-3-opus' | 'claude-3-sonnet';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  answer: string;
  sources: {
    title: string;
    content: string;
    url: string;
  }[];
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface Subheading {
  text: string;
  hasBullet: boolean;
  isNumbered: boolean;
  number?: number;
}

export interface MessageContent {
  text: string;
  headings: string[];
  subheadings: Subheading[];
  codeBlocks: string[];
} 