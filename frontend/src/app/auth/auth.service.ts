import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { OAuthErrorEvent, OAuthService, UserInfo } from 'angular-oauth2-oidc';
import { BehaviorSubject, combineLatest } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private _authenticated$ = new BehaviorSubject<boolean>(false);
  readonly authenticated$ = this._authenticated$.asObservable();

  private _administrator$ = new BehaviorSubject<boolean>(false);
  readonly administrator$ = this._administrator$.asObservable();

  private _loading$ = new BehaviorSubject<boolean>(true);
  readonly loading$ = this._loading$.asObservable();
  readonly loaded$ = this._loading$.asObservable().pipe(map((v) => !v));

  /**
   * Publishes `true` if and only if (a) all the asynchronous initial
   * login calls have completed or errorred, and (b) the user ended up
   * being authenticated.
   *
   * In essence, it combines:
   *
   * - the latest known state of whether the user is authorized
   * - whether the ajax calls for initial log in have all been done
   */
  readonly canActivateProtectedRoutes$ = combineLatest([
    this.authenticated$,
    this.loaded$,
  ]).pipe(map((values) => values.every((b) => b)));

  readonly canActivateAdministrativeRoutes$ = combineLatest([
    this.authenticated$,
    this.administrator$,
    this.loaded$,
  ]).pipe(map((values) => values.every((b) => b)));

  private navigateToHomePage() {
    this.router.navigateByUrl('/');
  }

  constructor(private oauthService: OAuthService, private router: Router) {
    if (environment.auth.debug) {
      this.oauthService.events.subscribe((event) => {
        if (event instanceof OAuthErrorEvent) {
          console.error('OAuthErrorEvent Object:', event);
        } else {
          console.warn('OAuthEvent Object:', event);
        }
      });
    }

    // This is tricky, as it might cause race conditions (where access_token is set in another
    // tab before everything is said and done there.
    // TODO: Improve this setup. See: https://github.com/jeroenheijmans/sample-angular-oauth2-oidc-with-auth-guards/issues/2
    window.addEventListener('storage', (event) => {
      // The `key` is `null` if the event was caused by `.clear()`
      if (event.key !== 'access_token' && event.key !== null) {
        return;
      }

      console.warn(
        'Noticed changes to access_token (most likely from another tab), updating isAuthenticated'
      );
      this._authenticated$.next(this.oauthService.hasValidAccessToken());

      if (!this.oauthService.hasValidAccessToken()) {
        this.navigateToHomePage();
      }
    });

    this.oauthService.events.subscribe((_) => {
      this._authenticated$.next(this.oauthService.hasValidAccessToken());

      this._administrator$.next(
        this.oauthService.hasValidAccessToken() &&
          this.identity['groups'] &&
          this.identity['groups'].includes(environment.auth.adminGroup)
      );
    });

    this.oauthService.events
      .pipe(filter((e) => ['token_received'].includes(e.type)))
      .subscribe(() => this.oauthService.loadUserProfile());

    this.oauthService.events
      .pipe(
        filter((e) => ['session_terminated', 'session_error'].includes(e.type))
      )
      .subscribe(() => this.navigateToHomePage());

    this.oauthService.setupAutomaticSilentRefresh();
  }

  public init(): Promise<void> {
    if (location.hash && environment.auth.debug) {
      console.log('Encountered hash fragment, plotting as table...');
      console.table(
        location.hash
          .substr(1)
          .split('&')
          .map((kvp) => kvp.split('='))
      );
    }

    // 0. LOAD CONFIG:
    // First we have to check to see how the IdServer is
    // currently configured:
    return (
      this.oauthService
        .loadDiscoveryDocument()

        // 1. HASH LOGIN:
        // Try to log in via hash fragment after redirect back
        // from IdServer from initImplicitFlow:
        .then(() => this.oauthService.tryLogin())

        .then(() => {
          if (this.oauthService.hasValidAccessToken()) {
            return Promise.resolve();
          }

          // 2. SILENT LOGIN:
          // Try to log in via a refresh because then we can prevent
          // needing to redirect the user:
          return this.oauthService
            .silentRefresh()
            .then(() => Promise.resolve())
            .catch((result) => {
              // Subset of situations from https://openid.net/specs/openid-connect-core-1_0.html#AuthError
              // Only the ones where it's reasonably sure that sending the
              // user to the IdServer will help.
              const errorResponsesRequiringUserInteraction = [
                'interaction_required',
                'login_required',
                'account_selection_required',
                'consent_required',
              ];

              if (
                result &&
                result.reason &&
                errorResponsesRequiringUserInteraction.indexOf(
                  result.reason.error
                ) >= 0
              ) {
                // 3. ASK FOR LOGIN:
                // At this point we know for sure that we have to ask the
                // user to log in, so we redirect them to the IdServer to
                // enter credentials.
                //
                // Enable this to ALWAYS force a user to login.
                // this.login();
                //
                // Instead, we'll now do this:
                console.warn(
                  'User interaction is needed to log in, we will wait for the user to manually log in.'
                );
                return Promise.resolve();
              }

              // We can't handle the truth, just pass on the problem to the
              // next handler.
              return Promise.reject(result);
            });
        })

        .then(() => {
          this._loading$.next(false);

          // Check for the strings 'undefined' and 'null' just to be sure. Our current
          // login(...) should never have this, but in case someone ever calls
          // initImplicitFlow(undefined | null) this could happen.
          if (
            this.oauthService.state &&
            this.oauthService.state !== 'undefined' &&
            this.oauthService.state !== 'null'
          ) {
            let stateUrl = this.oauthService.state;

            if (!stateUrl.startsWith('/')) {
              stateUrl = decodeURIComponent(stateUrl);
            }

            if (environment.auth.debug) {
              console.log(
                `There was state of ${this.oauthService.state}, so we are sending you to: ${stateUrl}`
              );
            }

            this.router.navigateByUrl(stateUrl);
          }
        })
        .catch(() => this._loading$.next(false))
    );
  }

  login(targetUrl?: string) {
    this.oauthService.initLoginFlow(targetUrl || this.router.url);
  }

  logout() {
    this.oauthService.logOut();
  }

  get identity(): UserInfo {
    return <UserInfo>this.oauthService.getIdentityClaims();
  }

  get accessToken(): string {
    return this.oauthService.getAccessToken();
  }
}
