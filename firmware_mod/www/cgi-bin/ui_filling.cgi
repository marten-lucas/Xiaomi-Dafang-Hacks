#!/bin/sh

. /system/sdcard/www/cgi-bin/func.cgi
. /system/sdcard/scripts/common_functions.sh

export LD_LIBRARY_PATH=/system/lib
export LD_LIBRARY_PATH=/thirdlib:$LD_LIBRARY_PATH

echo "Content-type: text"
echo "Pragma: no-cache"
echo "Cache-Control: max-age=0, no-store, no-cache"
echo ""

if [ -n "$F_cmd" ]; then
  case "$F_cmd" in
  get_config)
    if [ ! -f "/system/sdcard/config/filling.conf" ]; then
      $(cp /system/sdcard/config/filling.conf.dist /system/sdcard/config/filling.conf)
    fi
    source /system/sdcard/config/filling.conf
    echo "currentRegion#:#${region_of_interest}"
    echo "serverImage#:#${server_image}"
    echo "serverData#:#${server_data}"
    echo "serverDebug#:#${server_debug}"
    echo "thresholdMin#:#${threshold_min}"
    echo "thresholdMax#:#${threshold_max}"
    echo "levelLow#:#${level_low}"
    echo "levelMedium#:#${level_medium}"
    echo "colorLow#:#${color_low}"
    echo "colorMedium#:#${color_medium}"
    echo "colorFull#:#${color_full}"
    echo "colorBox#:#${color_box}"
    echo "fillingDetection#:#${filling_detection}"
    echo "updateInterval#:#${update_interval}"
    echo "containerCapacity#:#${container_capacity}"
    echo "mqttValueTopic#:#${mqtt_value_topic}"
    echo "zipOilprice#:#${zip_oilprice}"
    ;;

  save_config)
    if [ -n "${F_region+x}" ]; then
      F_region=$(printf '%b' "${F_region//%/\\x}")
      rewrite_config /system/sdcard/config/filling.conf region_of_interest "$F_region"
      echo "Region set to $F_region<br/>"
    fi
    if [ -n "${F_serverImage+x}" ]; then
      F_serverImage=$(printf '%b' "${F_serverImage//%/\\x}")
      rewrite_config /system/sdcard/config/filling.conf server_image "$F_serverImage"
      echo "Image server endpoint set to $F_serverImage<br/>"
    fi
    if [ -n "${F_serverData+x}" ]; then
      F_serverData=$(printf '%b' "${F_serverData//%/\\x}")
      rewrite_config /system/sdcard/config/filling.conf server_data "$F_serverData"
      echo "Data server endpoint set to $F_serverData<br/>"
    fi
    if [ -n "${F_serverDebug+x}" ]; then
      F_serverDebug=$(printf '%b' "${F_serverDebug//%/\\x}")
      rewrite_config /system/sdcard/config/filling.conf server_debug "$F_serverDebug"
      echo "Debug server endpoint set to $F_serverDebug<br/>"
    fi
    if [ -n "${F_thresholdMin+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf threshold_min "$F_thresholdMin"
      echo "Threshold Min set to $F_thresholdMin<br/>"
    fi
    if [ -n "${F_thresholdMax+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf threshold_max "$F_thresholdMax"
      echo "Threshold Max set to $F_thresholdMax<br/>"
    fi
    if [ -n "${F_levelLow+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf level_low "$F_levelLow"
      echo "Level Low set to $F_levelLow<br/>"
    fi
    if [ -n "${F_levelMedium+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf level_medium "$F_levelMedium"
      echo "Level Medium set to $F_levelMedium<br/>"
    fi
    if [ -n "${F_colorLow+x}" ]; then
      F_colorLow=$(printf '%b' "${F_colorLow//%/\\x}")
      rewrite_config /system/sdcard/config/filling.conf color_low "$F_colorLow"
      echo "Color Low set to $F_colorLow<br/>"
    fi
    if [ -n "${F_colorMedium+x}" ]; then
      F_colorMedium=$(printf '%b' "${F_colorMedium//%/\\x}")
      rewrite_config /system/sdcard/config/filling.conf color_medium "$F_colorMedium"
      echo "Color Medium set to $F_colorMedium<br/>"
    fi
    if [ -n "${F_colorFull+x}" ]; then
      F_colorFull=$(printf '%b' "${F_colorFull//%/\\x}")
      rewrite_config /system/sdcard/config/filling.conf color_full "$F_colorFull"
      echo "Color Full set to $F_colorFull<br/>"
    fi
    if [ -n "${F_colorBox+x}" ]; then
      F_colorBox=$(printf '%b' "${F_colorBox//%/\\x}")
      rewrite_config /system/sdcard/config/filling.conf color_box "$F_colorBox"
      echo "Color Box set to $F_colorBox<br/>"
    fi

    if [ -n "${F_fillingDetection+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf filling_detection "$F_fillingDetection"
      echo "Filling Detection set to $F_fillingDetection<br/>"
    fi
    if [ -n "${F_updateInterval+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf update_interval "$F_updateInterval"
      echo "Update Interval set to $F_updateInterval<br/>"
    fi
    if [ -n "${F_containerCapacity+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf container_capacity "$F_containerCapacity"
      echo "Container Capacity set to $F_containerCapacity<br/>"
    fi
    if [ -n "${F_mqttValueTopic+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf mqtt_value_topic "$F_mqttValueTopic"
      echo "MQTT Value Topic set to $F_mqttValueTopic<br/>"
    fi
    if [ -n "${F_zipOilprice+x}" ]; then
      rewrite_config /system/sdcard/config/filling.conf zip_oilprice "$F_zipOilprice"
      echo "ZIP Code for Oilprice set to $F_zipOilprice<br/>"
    fi
    ;;

  *)
    echo "Unsupported command '$F_cmd'"
    ;;
  esac
fi

exit 0
