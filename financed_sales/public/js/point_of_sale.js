frappe.provide("erpnext.pos");

(function() {
  function addCustomButton() {
    // only once
    if (document.getElementById('my-custom-btn')) return;

    // this is the one that works
    const container = document.querySelector('.cart-container');
    if (!container) return;

    const btn = document.createElement('button');
    btn.id = 'my-custom-btn';
    btn.innerText = __('My Button');
    btn.className = 'btn btn-primary btn-sm';
    // ensure it sits on top and is clickable
    btn.style.position      = 'relative';
    btn.style.zIndex        = '9999';
    btn.style.pointerEvents = 'auto';

    btn.onclick = () => {
      frappe.msgprint(__('You clicked My Button!'));
      return false;
    };

    container.appendChild(btn);
  }

  // catch it immediately if already rendered
  addCustomButton();

  // catch any later re-renders
  const observer = new MutationObserver(addCustomButton);
  observer.observe(document.body, { childList: true, subtree: true });

  // safety net after ajax loads
  frappe.after_ajax(addCustomButton);
})();

