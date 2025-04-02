import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function generateMessageId(): string {
  // Generate a unique ID using timestamp and random number
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000000);
  return `msg-${timestamp}-${random}`;
}
