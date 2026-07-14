-- https://github.com/Rheinmir/lume/issues/4322
ALTER TABLE `resource` MODIFY `reference` TEXT NOT NULL DEFAULT ('');
