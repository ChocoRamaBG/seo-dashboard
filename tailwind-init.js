const { exec } = require('child_process');

// На Windows използваме tailwindcss.cmd
exec('node_modules\\.bin\\tailwindcss.cmd init -p', (err, stdout, stderr) => {
  if (err) {
    console.error(`Error: ${err}`);
    return;
  }
  console.log(stdout);
  console.error(stderr);
});