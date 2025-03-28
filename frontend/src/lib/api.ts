import { ChatResponse } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function sendMessage(message: string): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: [
          {
            role: 'user',
            content: message,
          },
        ],
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || 
        `Failed to send message: ${response.status} ${response.statusText}`
      );
    }

    const data = await response.json();
    return {
      answer: data.content,
      sources: data.sources.map((source: any) => ({
        title: source.name,
        content: source.content,
        url: source.url || '',
      })),
    };
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`API Error: ${error.message}`);
    }
    throw new Error('An unexpected error occurred while sending the message');
  }
} 