import { Component, ElementRef, EventEmitter, HostListener, OnInit, Output, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'ema-textbox-multi-select',
  templateUrl: './textbox-multi-select.component.html',
  styleUrls: ['./textbox-multi-select.component.scss']
})
export class TextboxMultiSelectComponent implements OnInit {
  @Output() onSearchChanged = new EventEmitter();

  textboxMultiSelectForm = new FormGroup({
    inputControl: new FormControl('')
  });

  tagList = [];

  @HostListener('click') onClick() {
    this.el.nativeElement.querySelector('input').focus();
  };

  constructor(private readonly el: ElementRef) { }

  ngOnInit(): void {
  }

  textEntered() {
    let inputControl = this.textboxMultiSelectForm.get('inputControl');
    let textValue = inputControl.value;
    if (textValue.length > 0 && this.tagList.filter((tag) => tag == textValue).length === 0) {
      this.tagList.push(inputControl.value)
    }
    inputControl.reset();
    this.onSearchChanged.emit({keyList:[...this.tagList], operation:'add'});
  }

  clearAllTags() {
    this.tagList = [];
    this.onSearchChanged.emit({keyList:[...this.tagList], operation:'clearAll'});
  }

  deleteTag(event) {
    for (let i = 0; i < this.tagList.length; i++) {
      if (this.tagList[i] == event.name) {
        this.tagList.splice(i, 1);
      }
    }
    this.onSearchChanged.emit({keyToDelete: event.name, operation:'clearSelected'});
  }
}