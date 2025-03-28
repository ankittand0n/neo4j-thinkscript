export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
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