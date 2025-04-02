'use client';

import { useEffect, useRef, useState } from 'react';
import { ChatMessage } from './message';
import { ChatInput } from './input';
import { Message, ChatState } from '@/types/chat';
import { sendMessage, AIModel } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { loadChatHistory, saveChatHistory, clearChatHistory } from '@/lib/storage';
import { Trash2 } from 'lucide-react';
import { generateMessageId } from '@/lib/utils';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface ChatProps {
  initialState?: ChatState;
}

export function Chat({ initialState }: ChatProps) {
  const [mounted, setMounted] = useState(false);
  const [state, setState] = useState<ChatState>(() => ({
    messages: [],
    isLoading: false,
    error: null,
    ...initialState,
  }));
  const [selectedModel, setSelectedModel] = useState<AIModel>('gpt-3.5-turbo');
  const [streamingContent, setStreamingContent] = useState('');
  const streamingMessageId = useRef<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const lastFailedMessage = useRef<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load chat history after component mounts
  useEffect(() => {
    setMounted(true);
    setState(prev => ({
      ...prev,
      messages: loadChatHistory(),
    }));
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [state.messages, streamingContent]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (mounted) {
      saveChatHistory(state.messages);
    }
  }, [state.messages, mounted]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, streamingContent]);

  const handleSend = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: generateMessageId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      // Create assistant message with empty content
      const assistantMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
      };

      // Add assistant message to state
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
      }));

      // Send message and handle streaming response
      await sendMessage([...state.messages, userMessage], (chunk) => {
        setStreamingContent(prev => prev + chunk);
        // Update the assistant message content
        setState(prev => ({
          ...prev,
          messages: prev.messages.map(msg => 
            msg.id === assistantMessage.id
              ? { ...msg, content: msg.content + chunk }
              : msg
          ),
        }));
      }, selectedModel);

      // Update final state
      setState(prev => ({
        ...prev,
        isLoading: false,
      }));

      // Clean up streaming state
      setStreamingContent('');
      lastFailedMessage.current = null;
    } catch (error) {
      console.error('Error sending message:', error);
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to send message. Please try again.',
      }));
      setStreamingContent('');
      lastFailedMessage.current = content;
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
    setStreamingContent('');
    streamingMessageId.current = null;
  };

  if (!mounted) {
    return null;
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex justify-between items-center p-2 border-b">
        <Select value={selectedModel} onValueChange={(value: AIModel) => setSelectedModel(value)}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select AI Model" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo (Fast)</SelectItem>
            <SelectItem value="gpt-4-turbo-preview">GPT-4 Turbo (More Capable)</SelectItem>
          </SelectContent>
        </Select>
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
            <div ref={messagesEndRef} />
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