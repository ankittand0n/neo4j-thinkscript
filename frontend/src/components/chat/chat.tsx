'use client';

import { useEffect, useRef, useState } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage } from './message';
import { ChatInput } from './input';
import { Message, ChatState } from '@/types/chat';
import { sendMessage } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { loadChatHistory, saveChatHistory, clearChatHistory } from '@/lib/storage';
import { Trash2 } from 'lucide-react';

interface ChatProps {
  initialState?: ChatState;
}

export function Chat({ initialState }: ChatProps) {
  const [state, setState] = useState<ChatState>(() => ({
    messages: loadChatHistory(),
    isLoading: false,
    error: null,
    ...initialState,
  }));

  const scrollRef = useRef<HTMLDivElement>(null);
  const lastFailedMessage = useRef<string | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [state.messages]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    saveChatHistory(state.messages);
  }, [state.messages]);

  const handleSend = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
    };

    setState((prev: ChatState) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      const response = await sendMessage(content);
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        content: response.answer,
        role: 'assistant',
        timestamp: new Date().toISOString(),
      };

      setState((prev: ChatState) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));
      lastFailedMessage.current = null;
    } catch (error) {
      lastFailedMessage.current = content;
      setState((prev: ChatState) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to send message. Please try again.',
      }));
    }
  };

  const handleRetry = () => {
    if (lastFailedMessage.current) {
      handleSend(lastFailedMessage.current);
    }
  };

  const handleClearHistory = () => {
    clearChatHistory();
    setState((prev: ChatState) => ({
      ...prev,
      messages: [],
      error: null,
    }));
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex justify-end p-2 border-b">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleClearHistory}
          className="text-muted-foreground hover:text-destructive"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Clear History
        </Button>
      </div>
      <div className="flex-1 min-h-0">
        <div ref={scrollRef} className="h-full overflow-y-auto p-4">
          <div className="space-y-4 pb-4">
            {state.messages.map((message: Message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {state.error && (
              <div className="rounded-md bg-destructive/15 p-4 text-sm text-destructive space-y-2">
                <p>{state.error}</p>
                {lastFailedMessage.current && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRetry}
                    className="mt-2"
                  >
                    Retry
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="sticky bottom-0 border-t bg-white">
        <ChatInput onSend={handleSend} isLoading={state.isLoading} />
      </div>
    </div>
  );
} 