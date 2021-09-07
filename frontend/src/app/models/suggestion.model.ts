import { Identity } from './identity.model';

export declare class Suggestion {
  id: string;
  created_at: string;
  updated_at: string;
  identity: Identity | null;
  score: number | null;
}
