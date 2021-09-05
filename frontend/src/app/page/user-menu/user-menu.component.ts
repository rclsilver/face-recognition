import { Component } from '@angular/core';
import { UserInfo } from 'angular-oauth2-oidc';
import { AuthService } from 'src/app/auth/auth.service';

@Component({
  selector: 'app-user-menu',
  templateUrl: './user-menu.component.html',
  styleUrls: ['./user-menu.component.scss'],
})
export class UserMenuComponent {
  readonly authenticated$ = this._auth.authenticated$;

  constructor(private _auth: AuthService) {}

  login(): void {
    this._auth.login();
  }

  logout(): void {
    this._auth.logout();
  }

  get identity(): UserInfo {
    return this._auth.identity;
  }
}
