import { Message } from '@/types/chat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type AIModel = 'gpt-3.5-turbo' | 'gpt-4-turbo-preview';

export async function sendMessage(
  messages: Message[], 
  onChunk: (chunk: string) => void,
  model: AIModel = 'gpt-3.5-turbo'
): Promise<void> {
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ messages, model }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch');
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          if (data.error) {
            throw new Error(data.error);
          }
          if (data.content) {
            onChunk(data.content);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
} 