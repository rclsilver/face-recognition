import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TestWebcamComponent } from './test-webcam/test-webcam.component';

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

@NgModule({
  declarations: [
    AppComponent,
    TestWebcamComponent,
    TopMenuComponent,
    IdentityListComponent,
    LearnComponent,
    QueryComponent,
    WebcamComponent,
    ResultComponent,
    IdentityFormComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    WebcamModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
