import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { WebcamModule } from 'ngx-webcam';
import { HttpClientModule } from '@angular/common/http';
import { TopMenuComponent } from './page/top-menu/top-menu.component';
import { IdentityListComponent } from './identities/identity-list/identity-list.component';
import { LearnComponent } from './recognition/learn/learn.component';
import { QueryComponent } from './recognition/query/query.component';
import { WebcamComponent } from './recognition/webcam/webcam.component';
import { ResultComponent } from './recognition/result/result.component';
import { IdentityFormComponent } from './identities/identity-form/identity-form.component';
import { FormsModule } from '@angular/forms';
import { CameraListComponent } from './cameras/camera-list/camera-list.component';
import { CameraFormComponent } from './cameras/camera-form/camera-form.component';
import { CameraLiveComponent } from './cameras/camera-live/camera-live.component';
import { UserListComponent } from './users/user-list/user-list.component';
import { AuthModule } from './auth/auth.module';
import { UserMenuComponent } from './page/user-menu/user-menu.component';
import { QueryListComponent } from './queries/query-list/query-list.component';

@NgModule({
  declarations: [
    AppComponent,
    TopMenuComponent,
    IdentityListComponent,
    LearnComponent,
    QueryComponent,
    WebcamComponent,
    ResultComponent,
    IdentityFormComponent,
    CameraListComponent,
    CameraFormComponent,
    CameraLiveComponent,
    UserListComponent,
    UserMenuComponent,
    QueryListComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    WebcamModule,
    AuthModule.forRoot(),
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
