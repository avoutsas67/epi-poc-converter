import { Component, ElementRef, EventEmitter, HostListener, Input, OnInit, Output } from '@angular/core';
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
  @Input()
  tagList = [];

  @Input()
  isSmall = false;

  @Input()
  hideClearSearch = false;

  @Input()
  isSingleSelect = false;

  @HostListener('click') onClick() {
    if(!(this.isSingleSelect && this.tagList.length > 0)){
      this.el.nativeElement.querySelector('input').focus();
    }
  };

  constructor(private readonly el: ElementRef) { }

  ngOnInit(): void {
  }

  textEntered() {
    let inputControl = this.textboxMultiSelectForm.get('inputControl');
    let textValue = inputControl.value;
    if (textValue && textValue?.length > 0 && this.tagList.filter((tag) => tag.toLowerCase() == textValue.toLowerCase()).length === 0) {
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
    this.onSearchChanged.emit({keyList:[...this.tagList], keyToDelete: event.name, operation:'clearSelected'});
  }
}
