import { Component } from '@angular/core';
import { of } from 'rxjs';
import { AuthService } from 'src/app/auth/auth.service';

@Component({
  selector: 'app-top-menu',
  templateUrl: './top-menu.component.html',
  styleUrls: ['./top-menu.component.scss'],
})
export class TopMenuComponent {
  readonly items = [
    {
      label: 'Identities',
      path: 'identities',
      allowed$: this._auth.authenticated$,
    },
    {
      label: 'Cameras',
      path: 'cameras',
      allowed$: this._auth.authenticated$,
    },
    {
      label: 'Query',
      path: 'recognition/query',
      allowed$: of(true),
    },
    {
      label: 'Learn',
      path: 'recognition/learn',
      allowed$: this._auth.authenticated$,
    },
    {
      label: 'Users',
      path: 'users',
      allowed$: this._auth.authenticated$,
    },
  ];

  constructor(private _auth: AuthService) {}
}
