import helper from "./helper";

export function renderApp(name) {
  return helper(name);
}

class Widget {
  draw(ctx) {
    return ctx;
  }
}
