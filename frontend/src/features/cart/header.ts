import { cart } from "./store";
function update() {
  const total = cart.read().reduce((sum, item) => sum + item.quantity, 0);
  document
    .querySelectorAll("[data-cart-count]")
    .forEach((el) => (el.textContent = String(total)));
}
window.addEventListener("beront:cart", update);
window.addEventListener("storage", () => {
  cart.invalidate();
  update();
});
update();
if (document.getElementById("cart-dialog")) void import("./dialog");
