const navItemDropDownList = document.querySelectorAll('.nav-item-dropdown');

navItemDropDownList.forEach((navItem) => {
  navItem.addEventListener('click', () => {
    console.log(navItem);
  })
})