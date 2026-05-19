import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';

import { AppComponent } from './app.component';

describe('AppComponent', () => {
  let fixture: ComponentFixture<AppComponent>;
  let component: AppComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AppComponent],
      imports: [FormsModule, HttpClientTestingModule],
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('renders the page title', () => {
    const title = fixture.nativeElement.querySelector('h1');

    expect(title?.textContent).toContain('Github Analyzer');
  });

  it('shows the placeholder error after search', () => {
    component.search();
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('p');

    expect(message?.textContent).toContain('Search is not wired yet.');
  });
});
