import {
  ModuleWithProviders,
  NgModule,
  Optional,
  SkipSelf,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  AuthConfig,
  OAuthModule,
  OAuthModuleConfig,
  OAuthStorage,
} from 'angular-oauth2-oidc';
import { environment } from 'src/environments/environment';
import { AuthService } from './auth.service';
import { RequireUserGuard } from './guards/require-user.guard';
import { RequireAdminGuard } from './guards/require-admin.guard';
import { HttpClientModule } from '@angular/common/http';

export function storageFactory(): OAuthStorage {
  return localStorage;
}

@NgModule({
  declarations: [],
  imports: [CommonModule, HttpClientModule, OAuthModule.forRoot()],
  providers: [AuthService, RequireUserGuard, RequireAdminGuard],
})
export class AuthModule {
  static forRoot(): ModuleWithProviders<AuthModule> {
    return {
      ngModule: AuthModule,
      providers: [
        {
          provide: AuthConfig,
          useValue: {
            issuer: environment.auth.issuer,
            clientId: environment.auth.clientId,
            responseType: 'code',
            redirectUri: window.location.origin + '/index.html',
            silentRefreshRedirectUri: `${window.location.origin}/silent-refresh.html`,
            useSilentRefresh: true,
            scope: 'openid profile offline_access',
            sessionChecksEnabled: true,
            showDebugInformation: environment.auth.debug,
            clearHashAfterLogin: false,
            nonceStateSeparator: 'semicolon',
          },
        },
        {
          provide: OAuthModuleConfig,
          useValue: {
            resourceServer: {
              allowedUrls: ['/api'],
              sendAccessToken: true,
            },
          },
        },
        {
          provide: OAuthStorage,
          useFactory: storageFactory,
        },
      ],
    };
  }

  constructor(@Optional() @SkipSelf() parentModule: AuthModule) {
    if (parentModule) {
      throw new Error(
        'AuthModule is already loaded. Import it in the AppModule only'
      );
    }
  }
}
