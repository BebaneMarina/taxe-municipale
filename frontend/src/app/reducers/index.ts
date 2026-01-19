import { isDevMode } from '@angular/core';
import {
  ActionReducer,
  ActionReducerMap,
  createFeatureSelector,
  createSelector,
  MetaReducer
} from '@ngrx/store';
import {counterReducer} from '../ngrx/counter/counter.reducer';
import {UserInterface} from '../interfaces/user.interface';
import {userReducer} from '../ngrx/user/user.reducer';

export interface AppState {
  counter: number;
  user : UserInterface;
}

export const reducers: ActionReducerMap<AppState> = {
  counter: counterReducer,
  user: userReducer,
};


export const metaReducers: MetaReducer<AppState>[] = isDevMode() ? [] : [];
