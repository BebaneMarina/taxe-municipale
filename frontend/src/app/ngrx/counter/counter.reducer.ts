import {createReducer, on} from '@ngrx/store';
import {counterState} from './counter.state';
import {decrement, increment, multiply} from './counter.action';

export const counterReducer = createReducer(
  counterState,
  on(increment, (state, payload) => state + 1),
  on(decrement, (state, payload) => state - 1),
  on(multiply, (state) => state * 2),
);
