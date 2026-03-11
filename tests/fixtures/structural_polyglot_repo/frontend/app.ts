import { helper } from "./helper";

export class TypeWidget {
  run(value: string): number {
    return value.length;
  }
}

export function typedEntry(arg: string): number {
  return helper(arg);
}
