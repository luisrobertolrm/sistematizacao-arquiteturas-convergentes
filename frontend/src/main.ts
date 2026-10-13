import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { bootstrapApplication } from '@angular/platform-browser';
import { App } from './app/app';
import { autenticacaoInterceptor } from './app/core/api';

bootstrapApplication(App, { providers: [provideHttpClient(withInterceptors([autenticacaoInterceptor]))] })
  .catch((error: unknown) => { console.error('Não foi possível iniciar a aplicação.', error); });
