import { NgModule } from '@angular/core';
import { ExtraOptions, RouterModule, Routes } from '@angular/router';
import { IdentityListComponent } from './identities/identity-list/identity-list.component';
import { LearnComponent } from './recognition/learn/learn.component';
import { QueryComponent } from './recognition/query/query.component';

const routes: Routes = [
  {
    path: 'identities',
    children: [
      {
        path: '',
        component: IdentityListComponent,
      },
    ],
  },
  {
    path: 'recognition',
    children: [
      {
        path: 'learn',
        component: LearnComponent,
      },
      {
        path: 'query',
        component: QueryComponent,
      },
    ],
  },
];

const config: ExtraOptions = {
  useHash: true,
};

@NgModule({
  imports: [RouterModule.forRoot(routes, config)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
