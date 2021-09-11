import { Identity } from "./identity.model";
import { Rect } from "./rect.model";

export declare class Recognition {
  identity: Identity | null;
  score: number | null;
  rect: Rect;
}
