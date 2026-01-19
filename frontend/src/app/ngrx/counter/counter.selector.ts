import {createSelector} from '@ngrx/store';
import {AppState} from '../../reducers';

export const counterSelector = createSelector((app : AppState) => app.counter,state => state);
