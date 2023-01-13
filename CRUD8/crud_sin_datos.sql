SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

START TRANSACTION;

SET time_zone = "+00:00";

CREATE TABLE `unidades` (
  `id` int(11) NOT NULL,
  `descripcion` varchar(40) NOT NULL,
  `abreviatura` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `presentaciones` (
  `id` int(11) NOT NULL,
  `descripcion` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `grupos` (
  `id` int(11) NOT NULL,
  `descripcion` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `id_grupo` int(11) NOT NULL,
  `id_unidad` int(11) NOT NULL,
  `descripcion` varchar(45) NOT NULL,
  `fotoBase64` longtext DEFAULT NULL,
  `stock_min` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `envases` (
  `id` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `id_presentacion` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `stock` (
  `id` int(11) NOT NULL,
  `id_envase` int(11) NOT NULL,
  `fecha_vencimiento` date NOT NULL,
  `fecha_compra` date NOT NULL,
  `fecha_uso` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE VIEW `prod_pres` AS 
 SELECT `e`.`id` AS `id`, 
        concat(`prod`.`descripcion`,' ',`pres`.`descripcion`,' ',`e`.`cantidad`,' ',`u`.`abreviatura`) AS `descripcion`, 
        `e`.`cantidad` AS `cantidad_unitaria`, 
        `e`.`cantidad`* ifnull((select count(1)
                                 from `stock`
                                 where `stock`.`id_envase` = `e`.`id`),0) AS `cantidad_total`,
        `prod`.`id` AS `id_producto`,
        `pres`.`id` AS `id_presentacion`, 
        `u`.`id` AS `id_unidad`, 
        `prod`.`fotoBase64` AS `fotobase64`
 FROM (((`productos` `prod` join `presentaciones` `pres`) join `envases` `e`) join `unidades` `u`)
 WHERE `pres`.`id` = `e`.`id_presentacion`
   AND `prod`.`id` = `e`.`id_producto`
   AND `prod`.`id_unidad` = `u`.`id` ;

ALTER TABLE `unidades`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `presentaciones`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `grupos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `descripcion_UNIQUE` (`descripcion`) USING BTREE;

ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `descripcion_UNIQUE` (`descripcion`),
  ADD KEY `FK_producto_grupo` (`id_grupo`),
  ADD KEY `FK_producto_unidad` (`id_unidad`);

ALTER TABLE `envases`
  ADD PRIMARY KEY (`id`),
  ADD KEY `FK_envase_producto` (`id_producto`),
  ADD KEY `FK_envase_presentacion` (`id_presentacion`);

ALTER TABLE `stock`
  ADD PRIMARY KEY (`id`),
  ADD KEY `FK_stock_envase` (`id_envase`);

ALTER TABLE `unidades`       MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
ALTER TABLE `presentaciones` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
ALTER TABLE `grupos`         MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
ALTER TABLE `productos`      MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
ALTER TABLE `envases`        MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
ALTER TABLE `stock`          MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

ALTER TABLE `productos`
  ADD CONSTRAINT `FK_producto_grupo` FOREIGN KEY (`id_grupo`) REFERENCES `grupos` (`id`),
  ADD CONSTRAINT `FK_producto_unidad` FOREIGN KEY (`id_unidad`) REFERENCES `unidades` (`id`);

ALTER TABLE `envases`
  ADD CONSTRAINT `FK_envase_presentacion` FOREIGN KEY (`id_presentacion`) REFERENCES `presentaciones` (`id`),
  ADD CONSTRAINT `FK_envase_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id`);

ALTER TABLE `stock`
  ADD CONSTRAINT `FK_stock_envase` FOREIGN KEY (`id_envase`) REFERENCES `envases` (`id`);

COMMIT;
