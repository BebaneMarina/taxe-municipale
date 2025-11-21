import {createReducer, on} from '@ngrx/store';
import {userState} from './user.state';
import {login} from './user.action';

export const userReducer = createReducer(
  userState,
  on(login, (state,payload) => {
    return state;
  })
)
