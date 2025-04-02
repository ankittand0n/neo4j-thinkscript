import { Message } from '@/types/chat';

const CHAT_HISTORY_KEY = 'thinkscript_chat_history';

export function loadChatHistory(): Message[] {
  if (typeof window === 'undefined') return [];
  
  try {
    const savedHistory = localStorage.getItem(CHAT_HISTORY_KEY);
    return savedHistory ? JSON.parse(savedHistory) : [];
  } catch (error) {
    console.error('Error loading chat history:', error);
    return [];
  }
}

export function saveChatHistory(messages: Message[]): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messages));
  } catch (error) {
    console.error('Error saving chat history:', error);
  }
}

export function clearChatHistory(): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.removeItem(CHAT_HISTORY_KEY);
  } catch (error) {
    console.error('Error clearing chat history:', error);
  }
} 